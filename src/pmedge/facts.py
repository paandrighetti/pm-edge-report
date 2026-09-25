"""Every figure the report prints, read from the source outputs.

Each fact records the file it came from. Statements the report makes in words (a sign, a
significance, "every cell") are checked here with `claim`; if a regenerated source
contradicts one, the build fails instead of printing a sentence the data no longer supports.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from decimal import ROUND_HALF_UP, Decimal
from dataclasses import dataclass, field
from pathlib import Path

from .tables import fixed_width, md_table, md_tables_after, num, read, text_section

ROOT = Path(__file__).resolve().parents[2]
SERVER = ROOT / "sources" / "server-20260923T2149Z"
BACKTEST = ROOT / "sources" / "pm-backtest-c8c343a" / "2026-09-18.md"
UPDOWN_README = ROOT / "sources" / "updown-desk-547d806" / "README.md"
KALSHI = ROOT / "sources" / "kalshi-20260924T1145Z"
KALSHI_SENS = ROOT / "sources" / "kalshi-sensitivity-20260924" / "0014-kalshi-late-settlement.log"
KALSHI_HORIZON = ROOT / "sources" / "kalshi-horizon-20260924" / "0015-kalshi-horizon.log"
KALSHI_NOW = ROOT / "sources" / "kalshi-20260925T1248Z"
KALSHI_STATUS = ROOT / "sources" / "kalshi-status-20260925"


class ClaimError(AssertionError):
    pass


@dataclass
class Facts:
    values: dict[str, str] = field(default_factory=dict)
    raw: dict[str, float | int | str | bool] = field(default_factory=dict)
    source: dict[str, str] = field(default_factory=dict)

    def put(self, key: str, value, fmt: str, src: Path) -> None:
        if key in self.values:
            raise KeyError(f"duplicate fact {key}")
        self.raw[key] = value
        self.values[key] = _fmt(value, fmt)
        self.source[key] = str(src.relative_to(ROOT))


def _fmt(value, fmt: str) -> str:
    """Format with half-up rounding on the decimal representation, so 0.245 prints 0.25."""
    if not fmt:
        return str(value)
    m = re.fullmatch(r"(.*)\{:(\+?)\.(\d)f\}(.*)", fmt)
    if m and isinstance(value, float):
        q = Decimal(repr(value)).quantize(Decimal(1).scaleb(-int(m.group(3))), rounding=ROUND_HALF_UP)
        body = f"{q:+f}" if m.group(2) else f"{q:f}"
        if body in ("-0", "+0") or re.fullmatch(r"[+-]0\.0+", body):
            body = body[1:] if not m.group(2) else "+" + body[1:]
        return m.group(1) + body + m.group(4)
    return fmt.format(value)


def claim(ok: bool, text: str) -> None:
    if not ok:
        raise ClaimError(f"source no longer supports: {text}")


def _t(x: float) -> str:
    return f"{x:+.1f}".replace("+", "") if x < 0 else f"{x:.1f}"


# --------------------------------------------------------------------------- updown-desk
def updown(f: Facts) -> None:
    src = SERVER / "updown-desk" / "latest.md"
    text = read(src)
    head = text.splitlines()[0]
    f.put("ud_report_head", head.lstrip("# ").strip(), "", src)

    feeds = {r["topic"]: num(r["agreement"]) for r in md_table(text, "## Which feed does the resolution follow")}
    n = int(num(md_table(text, "## Which feed does the resolution follow")[0]["n"]))
    f.put("ud_windows", n, "{:,}", src)
    f.put("ud_agree_twap60", feeds["crypto_prices_twap_sixty"] * 100, "{:.1f} %", src)
    f.put("ud_agree_twap30", feeds["crypto_prices_twap_thirty"] * 100, "{:.1f} %", src)
    f.put("ud_agree_chainlink", feeds["crypto_prices_chainlink"] * 100, "{:.1f} %", src)
    f.put("ud_agree_binance", feeds["crypto_prices"] * 100, "{:.1f} %", src)
    claim(max(feeds, key=feeds.get) == "crypto_prices_twap_sixty", "the 60 s TWAP is the best-agreeing feed")

    grid = md_table(text, "## Replay grid: fair-value taker, hold to resolution")
    pnl = [num(r["pnl_total"]) for r in grid]
    ts = [num(r["t_stat"]) for r in grid]
    fee_share = [num(r["fees"]) / -num(r["pnl_total"]) for r in grid]
    claim(all(p < 0 for p in pnl), "every taker cell loses")
    claim(all(num(r["pnl_total"]) + num(r["fees"]) < 0 for r in grid), "every taker cell still loses before fees")
    f.put("ud_taker_cells", len(grid), "{}", src)
    f.put("ud_taker_t_lo", min(ts), "{:.1f}", src)
    f.put("ud_taker_t_hi", max(ts), "{:.1f}", src)
    ns = [int(num(r["n"])) for r in grid]
    f.put("ud_taker_n_lo", min(ns), "{:,}", src)
    f.put("ud_taker_n_hi", max(ns), "{:,}", src)
    f.put("ud_taker_sig", sum(t < -2 for t in ts), "{}", src)
    f.put("ud_taker_nonsig", sum(t >= -2 for t in ts), "{}", src)
    zero_lat = [num(r["t_stat"]) for r in grid if r["latency_ms"] == "0"]
    claim(all(t < -2 for t in zero_lat), "the zero-latency cells, free of the fill-check bias, lose significantly")
    f.put("ud_fee_share_lo", min(fee_share) * 100, "{:.0f} %", src)
    f.put("ud_fee_share_hi", max(fee_share) * 100, "{:.0f} %", src)

    brier = {int(num(r["offset_s"])): r for r in md_table(text, "## Model versus market at fixed checkpoints")}
    f.put("ud_brier_n_840", int(num(brier[840]["n"])), "{:,}", src)
    for off in (300, 600, 840):
        f.put(f"ud_brier_model_{off}", num(brier[off]["brier_model"]), "{:.4f}", src)
        f.put(f"ud_brier_market_{off}", num(brier[off]["brier_market"]), "{:.4f}", src)
    late_better = all(num(brier[o]["brier_model"]) < num(brier[o]["brier_market"]) for o in (600, 840))
    claim(late_better, "the TWAP model has a lower Brier score than the mid at 10 and 14 minutes")
    claim(num(brier[300]["brier_model"]) > num(brier[300]["brier_market"]), "the mid beats the model at 5 minutes")

    cal = md_table(text, "### Calibration by model probability decile")
    top, bot = cal[-1], cal[0]
    for tag, row in (("top", top), ("bot", bot)):
        f.put(f"ud_cal_{tag}_model", num(row["model_p"]), "{:.3f}", src)
        f.put(f"ud_cal_{tag}_market", num(row["market_mid"]), "{:.3f}", src)
        f.put(f"ud_cal_{tag}_real", num(row["realized"]), "{:.3f}", src)
    claim(num(top["model_p"]) > num(top["realized"]) > num(top["market_mid"]),
          "in the top decile the model is overconfident and the mid underconfident")

    # v0.2 passive replay, still printed by the daily report
    pgrid = md_table(text, "## Passive quoting replay: two-sided quotes on the Up token, inventory held to resolution")
    claim(all(num(r["pnl_ex_rebate"]) < 0 and num(r["pnl"]) < 0 for r in pgrid), "every v0.2 passive cell loses")
    f.put("ud_v02_cells", len(pgrid), "{}", src)


def updown_readme(f: Facts) -> None:
    src = UPDOWN_README
    text = read(src)
    m = re.search(r"First results \(six days, ([\d ]+) resolved windows", text)
    f.put("ud0_windows", int(m.group(1).replace(" ", "")), "{:,}", src)
    m = re.search(r"agrees with the settled outcome ([\d.]+) % of the time\s+on `crypto_prices_twap_sixty`", text)
    f.put("ud0_agree_twap60", float(m.group(1)), "{:.1f} %", src)
    m = re.search(r"\(Brier ([\d.]+)\s+against ([\d.]+) at 14 minutes\)", text)
    f.put("ud0_brier_spot_840", float(m.group(1)), "{:.3f}", src)
    f.put("ud0_brier_mkt_840", float(m.group(2)), "{:.3f}", src)
    claim(float(m.group(1)) > float(m.group(2)), "the spot-settled model was worse than the market")


def passive(f: Facts) -> None:
    src = SERVER / "updown-desk" / "tape_study.txt"
    text = read(src)
    cov = {r["sample"]: r for r in fixed_width(text_section(text, 1))}
    f.put("ps_prints", sum(int(num(r["prints"])) for r in cov.values()), "{:,}", src)
    f.put("ps_windows", sum(int(num(r["windows"])) for r in cov.values()), "{:,}", src)
    f.put("ps_days", sum(int(num(r["days"])) for r in cov.values()), "{}", src)
    rs = {r["sample"]: r for r in fixed_width(text_section(text, 2))}
    for s, tag in (("exploration", "x"), ("confirmation", "c")):
        f.put(f"ps_rs30_{tag}", num(rs[s]["rs_30s"]), "{:+.2f}", src)
        f.put(f"ps_rs30_t_{tag}", num(rs[s]["t_rs_30s"]), "{:.1f}", src)
    claim(num(rs["exploration"]["rs_30s"]) < 0 < num(rs["confirmation"]["rs_30s"]),
          "the 30 s realized spread before rebate is negative then positive across samples")
    claim(abs(num(rs["confirmation"]["t_rs_30s"])) < 2, "the confirmation 30 s realized spread is not significant")
    claim(num(rs["exploration"]["t_rs_30s"]) < -2, "the exploration 30 s realized spread is a significant loss")

    buckets = fixed_width(text_section(text, 3))
    tested = len(buckets)
    passing = [b for b in buckets if num(b["exploration_t"]) > 2 and num(b["confirmation_t"]) > 2
               and num(b["exploration_cents"]) > 0 and num(b["confirmation_cents"]) > 0]
    claim(len(passing) == 1 and passing[0]["bucket"] == "[0.1, 0.3)", "exactly one bucket passes: distance 0.1 to 0.3")
    f.put("ps_buckets", tested, "{}", src)

    src_q = SERVER / "updown-desk" / "tape_queue.txt"
    q = fixed_width(text_section(read(src_q), 3))
    rows = {(r["sample"], r["prints"]): r for r in q}
    for s, tag in (("exploration", "x"), ("confirmation", "c")):
        allr, front, back = rows[(s, "all")], rows[(s, "front_or_middle")], rows[(s, "back")]
        f.put(f"pq_all_rs_{tag}", num(allr["rs_30s"]), "{:+.2f}", src_q)
        f.put(f"pq_all_stat_{tag}", num(allr["stat"]), "{:+.2f}", src_q)
        f.put(f"pq_rebate_{tag}", num(allr["rebate"]), "{:.2f}", src_q)
        f.put(f"pq_front_rs_{tag}", num(front["rs_30s"]), "{:+.2f}", src_q)
        f.put(f"pq_back_loss_{tag}", -num(back["rs_30s"]), "{:.2f}", src_q)
        f.put(f"pq_back_stat_{tag}", num(back["stat"]), "{:+.2f}", src_q)
        f.put(f"pq_back_stat_t_{tag}", num(back["t_stat"]), "{:.1f}", src_q)
        claim(num(back["t_stat"]) < 2, f"back-of-queue fills fail the rule ({s})")
        claim(num(front["rs_30s"]) > 0 > num(back["rs_30s"]), f"front fills earn and back fills lose the spread ({s})")


# --------------------------------------------------------------------------- pm-backtest
def backtest(f: Facts) -> None:
    src = BACKTEST
    text = read(src)
    head = text.splitlines()[2]
    f.put("bt_universe_line", head, "", src)
    m = re.search(r"Universe: (\d+) resolved markets, (\d+) in sample \(resolved before (\S+)\), (\d+) out of sample", head)
    f.put("bt_markets", int(m.group(1)), "{:,}", src)
    f.put("bt_is", int(m.group(2)), "{:,}", src)
    f.put("bt_split", m.group(3), "", src)
    f.put("bt_oos", int(m.group(4)), "{:,}", src)

    oos = md_table(text, "## favorite_carry", 1)[0]
    f.put("fc_n", int(num(oos["n"])), "{:,}", src)
    f.put("fc_loss", -num(oos["ret_per_trade"]) * 100, "{:.1f} %", src)
    f.put("fc_t", num(oos["t_stat"]), "{:.1f}", src)
    claim(num(oos["ret_per_trade"]) < 0 and num(oos["t_stat"]) < -2, "favorite carry loses out of sample")
    sens = {r["half_spread"]: r for r in md_table(text, "## favorite_carry", 3)}
    zero = sens["0.0000"]
    f.put("fc_loss_0", -num(zero["ret_per_trade"]) * 100, "{:.1f} %", src)
    f.put("fc_t_0", num(zero["t_stat"]), "{:.1f}", src)
    claim(num(zero["t_stat"]) < -2, "favorite carry loses even with zero half spread")
    cal = {r["bucket"]: r for r in md_table(text, "## favorite_carry", 2)}
    for b, tag in (("(0.95, 0.98]", "95"), ("(0.98, 1.0]", "98")):
        f.put(f"fc_mid_{tag}", num(cal[b]["avg_mid"]) * 100, "{:.1f} %", src)
        f.put(f"fc_win_{tag}", num(cal[b]["win_rate"]) * 100, "{:.1f} %", src)
        claim(num(cal[b]["win_rate"]) < num(cal[b]["avg_mid"]), f"favorites in {b} win less often than priced")

    db_side = {r["side"]: r for r in md_table(text, "## dutch_book", 4)}
    valid_oos = {r["side"]: r for r in md_table(text, "## dutch_book", 3)}
    f.put("db_no_several", num(valid_oos["no"]["share_several_winners"]) * 100, "{:.0f} %", src)
    f.put("db_yes_one", num(valid_oos["yes"]["share_one_winner"]) * 100, "{:.0f} %", src)
    f.put("db_yes_n", int(num(db_side["yes"]["n"])), "{}", src)
    f.put("db_yes_pnl", num(db_side["yes"]["pnl_total"]), "{:.0f}", src)
    claim(num(valid_oos["no"]["share_several_winners"]) > 0.5, "most NO books have several winners")
    db_is = md_table(text, "## dutch_book", 0)
    db_oos = md_table(text, "## dutch_book", 1)[0]
    selected = max(db_is, key=lambda r: num(r["t_stat"]))  # the report's selection rule
    f.put("db_is_roc", num(selected["return_on_capital"]) * 100, "{:.1f} %", src)
    f.put("db_yes_roc", num(db_side["yes"]["return_on_capital"]) * 100, "{:.0f} %", src)
    f.put("db_yes_t", num(db_side["yes"]["t_stat"]), "{:.1f}", src)
    f.put("db_no_roc", num(db_side["no"]["return_on_capital"]) * 100, "{:.1f} %", src)
    claim(num(db_side["yes"]["return_on_capital"]) > 0 and num(db_side["yes"]["t_stat"]) > 2,
          "the YES books keep a positive out-of-sample return")
    f.put("db_oos_roc", num(db_oos["return_on_capital"]) * 100, "{:.1f} %", src)
    claim(abs(num(db_oos["return_on_capital"])) < 0.005 < min(num(r["return_on_capital"]) for r in db_is),
          "the Dutch-book return on capital is positive in sample and flat out of sample")

    bh_is = md_table(text, "## binary_hedge", 0)
    best = max(bh_is, key=lambda r: num(r["t_stat"]))
    bh = md_table(text, "## binary_hedge", 1)[0]
    f.put("bh_cells", len(bh_is), "{}", src)
    f.put("bh_is_t", num(best["t_stat"]), "{:.1f}", src)
    f.put("bh_oos_loss", -num(bh["ret_per_trade"]) * 100, "{:.0f} %", src)
    f.put("bh_oos_t", num(bh["t_stat"]), "{:.1f}", src)
    f.put("bh_var_ratio", num(bh["var_ratio_hedged_over_unhedged"]), "{:.2f}", src)
    claim(num(best["t_stat"]) > 2 and num(bh["t_stat"]) < -2, "the best in-sample hedge cell reverses out of sample")


# --------------------------------------------------------------------------- pm-xarb
def xarb(f: Facts) -> None:
    src = SERVER / "pm-xarb" / "latest.md"
    text = read(src)
    f.put("xa_report_head", text.splitlines()[0].lstrip("# ").strip(), "", src)
    uni = {r["family"]: r for r in md_table(text, "## Universe")}
    exact = sum(int(num(r["exact"])) for r in uni.values() if r["exact"])
    basis = sum(int(num(r["basis"])) for r in uni.values() if r["basis"])
    k_legs = sum(int(num(r["kalshi_legs"])) for r in uni.values())
    k_unm = sum(int(num(r["kalshi_unmatched"])) for r in uni.values())
    f.put("xa_exact_pairs", exact, "{}", src)
    f.put("xa_basis_pairs", basis, "{}", src)
    f.put("xa_kalshi_unmatched", k_unm / k_legs * 100, "{:.0f} %", src)

    dq = md_table(text, "## Data quality")[0]
    f.put("xa_polls", int(num(dq["polls"])), "{:,}", src)
    f.put("xa_skew", num(dq["mean_skew_s"]), "{:.2f} s", src)

    det = [r for r in md_table(text, "## Detections (net of fees, depth-limited)") if r["klass"] == "exact"]
    f.put("xa_exact_det", sum(int(num(r["n"])) for r in det), "{}", src)
    f.put("xa_exact_edge_max", max(num(r["max_edge"]) for r in det) * 100, "{:.1f} cents", src)
    wmean = sum(num(r["mean_edge"]) * num(r["n"]) for r in det) / sum(num(r["n"]) for r in det)
    f.put("xa_exact_edge_mean", wmean * 100, "{:.1f} cents", src)
    ep = [r for r in md_table(text, "### Episodes (contiguous polls with the same opportunity)") if r["klass"] == "exact"][0]
    f.put("xa_exact_life_med", num(ep["median_life_s"]), "{:.0f} s", src)
    f.put("xa_exact_life_p90", num(ep["p90_life_s"]), "{:.0f} s", src)

    lf = md_table(text, "### Leg failures (second leg gone once the first is on; the cost sits in the unwinds)")[0]
    f.put("xa_fill_ratio", num(lf["fill_ratio"]) * 100, "{:.0f} %", src)

    since = {(r["family"], r["klass"]): r for r in md_table(text, "### Resolutions since inception")}
    se = since[("sports", "exact")]
    f.put("xa_exact_resolved", int(num(se["resolved_pairs"])), "{}", src)
    f.put("xa_exact_pnl", num(se["pnl"]), "{:.0f} USD", src)
    f.put("xa_exact_naked", int(num(se["naked_pairs"])), "{}", src)
    f.put("xa_exact_onesided", int(num(se["one_sided"])), "{}", src)
    f.put("xa_exact_naked_pnl", num(se["pnl_naked"]), "{:.0f} USD", src)
    f.put("xa_exact_hedged_pnl", num(se["pnl_hedged"]), "{:.0f} USD", src)
    sb = since[("crypto", "basis")]
    f.put("xa_basis_traded_pairs", int(num(sb["resolved_pairs"])), "{}", src)
    f.put("xa_basis_traded_pnl", num(sb["pnl"]), "{:.0f} USD", src)
    f.put("xa_basis_traded_onesided", int(num(sb["one_sided"])), "{}", src)
    f.put("xa_day", re.search(r"(\d{4}-\d{2}-\d{2})", text.splitlines()[0]).group(1), "", src)
    claim(num(se["pnl"]) < 0, "exact pairs lose since inception")

    cf = {r["klass"]: r for r in md_table(text, "## Classes not traded: counterfactual")}
    b = cf["basis"]
    e = cf["exact"]
    f.put("xa_exact_cf_pairs", int(num(e["pairs"])), "{}", src)
    f.put("xa_exact_cf_edge", num(e["mean_edge_at_entry"]) * 100, "{:.1f} cents", src)
    f.put("xa_exact_cf_pnl", num(e["mean_pnl_per_contract"]) * 100, "{:.1f} cents", src)
    claim(int(num(e["divergent"])) == 0 and num(e["mean_pnl_per_contract"]) > 0,
          "held without execution, exact pairs settle without divergence and at a small profit")
    f.put("xa_basis_cf_pairs", int(num(b["pairs"])), "{}", src)
    f.put("xa_basis_div", int(num(b["divergent"])), "{}", src)
    f.put("xa_basis_edge", num(b["mean_edge_at_entry"]) * 100, "{:.1f} cents", src)
    f.put("xa_basis_pnl", num(b["mean_pnl_per_contract"]) * 100, "{:.1f} cents", src)
    claim(num(b["mean_edge_at_entry"]) > num(e["mean_edge_at_entry"]), "basis pairs show more entry edge than exact pairs")
    claim(num(b["mean_edge_at_entry"]) > 0 > num(b["mean_pnl_per_contract"]),
          "basis pairs show a positive entry edge and a negative result")


# --------------------------------------------------------------------------- kalshi-maker
def kalshi(f: Facts) -> None:
    src = SERVER / "kalshi-maker" / "PREREGISTRATION.md"
    sha = hashlib.sha256(src.read_bytes()).hexdigest()
    f.put("km_prereg_sha", sha[:16], "", src)
    gate_path = KALSHI / "gate.json"
    if not gate_path.exists():
        f.put("km_status", "pending", "", src)
        return
    gate = json.loads(read(gate_path))
    primary = KALSHI / "reports" / "backtest" / "primary"
    summary_path, cells_path, volume_path = primary / "summary.json", primary / "cells.csv", primary / "volume.csv"
    summary = json.loads(read(summary_path))
    cells = list(csv.DictReader(cells_path.open(encoding="utf-8")))
    volume = list(csv.DictReader(volume_path.open(encoding="utf-8")))
    report_path = KALSHI / "reports" / "BACKTEST.md"
    report = read(report_path)
    prereg_path = KALSHI / "PREREGISTRATION.md"
    prereg = re.sub(r"\s+", " ", read(prereg_path))

    claim(gate["prereg_sha256"] == sha == hashlib.sha256(prereg_path.read_bytes()).hexdigest(),
          "the decision was taken under the pre-registration registered on 23 September, unchanged")
    claim(gate["valid"] and not gate["invalid_reasons"] and not gate["replication_fails"],
          "the data checks passed and the replication check did not fail")
    f.put("km_status", "decided", "", gate_path)
    f.put("km_gate_time", gate["generated_at"][:16].replace("T", " ") + " UTC", "", gate_path)
    qual = gate["qualifying"]
    f.put("km_pairs_tested", gate["pairs_tested"], "{}", gate_path)
    f.put("km_qualifying", len(qual), "{}", gate_path)
    claim(all(q["side"] == "short_yes" for q in qual), "every qualifying pair has the maker selling YES")
    p2 = 0.5 * math.erfc(2 / math.sqrt(2))  # P(t >= 2) for a standard normal t, one period
    f.put("km_expected_false", gate["pairs_tested"] * p2 * p2, "{:.2f}", gate_path)
    cats = sorted({q["category"] for q in qual})
    names = [c.lower() for c in cats]
    f.put("km_qual_cats", ", ".join(names[:-1]) + " and " + names[-1], "", gate_path)

    c = summary["counts"]
    f.put("km_trades", c["trades"], "{:,}", summary_path)
    f.put("km_trades_ok", c["trades_ok"], "{:,}", summary_path)
    f.put("km_trades_mve", c["trades_multivariate"], "{:,}", summary_path)
    f.put("km_trades_late", c["trades_late_expiration"], "{:,}", summary_path)
    f.put("km_events", c["events"], "{:,}", summary_path)
    f.put("km_flagged_all", c["markets_settled_after_latest_expiration"], "{:,}", summary_path)

    m = re.search(r"at least (\d+) clusters, (\d+) distinct events and (\d+) contracts, at least (\d+) clusters whose total is negative", prereg)
    floor_losing = int(m.group(4))
    f.put("km_floor_losing", floor_losing, "{}", prereg_path)

    rep = summary["replication_A_pooled"]
    f.put("km_rep_x", rep["exploration"]["mean_c"], "{:.2f}", summary_path)
    f.put("km_rep_c", rep["confirmation"]["mean_c"], "{:.2f}", summary_path)
    tmax = max(abs(t) for v in rep.values() for t in v["t_by_side"].values())
    f.put("km_rep_tmax", tmax, "{:.2f}", summary_path)
    claim(tmax < 2, "the pooled maker premium is not significant for either side in any period")
    claim(rep["confirmation"]["mean_c"] < rep["exploration"]["mean_c"], "the pooled premium is lower in the confirmation markets")

    by = {}
    for r in volume:
        by.setdefault(r["sample"], {})[r["category"]] = r
    for smp, tag in (("exploration", "x"), ("confirmation", "c")):
        total = sum(float(r["contracts"]) for r in by[smp].values())
        f.put(f"km_crypto_{tag}", float(by[smp]["Crypto"]["contracts"]) / total * 100, "{:.0f} %", volume_path)
    min_events = 100  # categories shown in the taker table: at least this many events in each period
    shown = [cat for cat in sorted(by["exploration"]) if cat in by["confirmation"]
             and min(float(by[smp][cat]["events"]) for smp in by) >= min_events]
    lines = ["| category | qualifying pair | exploration | confirmation |", "|---|---|---|---|"]
    for cat in shown:
        x, y = (float(by[smp][cat]["taker_yes_share"]) * 100 for smp in ("exploration", "confirmation"))
        lines.append(f"| {cat} | {'yes' if cat in cats else 'no'} | {_fmt(x, '{:.0f} %')} | {_fmt(y, '{:.0f} %')} |")
    f.put("km_taker_yes_table", "\n".join(lines), "", volume_path)
    claim(all(c in shown for c in cats), "every qualifying category is in the taker table")
    claim(any(c not in cats and min(float(by[smp][c]["taker_yes_share"]) for smp in by) > 0.5 for c in shown),
          "some category without a qualifying pair also has takers buying YES in most contracts")

    def cell(stat, smp, q):
        rows = [r for r in cells if r["stat"] == stat and r["sample"] == smp and r["category"] == q["category"]
                and r["side"] == q["side"] and r["bucket"] == str(q["bucket"])]
        claim(len(rows) == 1, f"one row per cell in cells.csv ({stat} {smp} {q['category']})")
        return rows[0]

    stat_of = {"PENNY": "B", "JOIN": "C"}
    edges = [0.0, 0.10, 0.30, 0.70, 0.90, 1.0]
    verdict_labels = {(r["variant"], r["category"], r["bucket"]) for r in md_table(report, "## Verdict")}

    def label(b):
        return f"[{edges[b]:.2f}, {edges[b + 1]:.2f})"

    lines = ["| variant | category | YES price | exploration: cents (t) | confirmation: cents (t) "
             "| every maker (A): exploration, confirmation | clusters (losing): exploration / confirmation |",
             "|---|---|---|---|---|---|---|"]
    changes = []
    losing_min = None
    for q in qual:
        claim((q["variant"], q["category"], label(q["bucket"])) in verdict_labels, "bucket labels match BACKTEST.md")
        st = stat_of[q["variant"]]
        ax, ac = cell("A", "exploration", q), cell("A", "confirmation", q)
        dx, dc = cell(st, "exploration", q), cell(st, "confirmation", q)
        claim(abs(float(dx["mean_c"]) - q["exploration_mean_c"]) < 1e-3 and abs(float(dc["mean_c"]) - q["confirmation_mean_c"]) < 1e-3,
              "gate.json and cells.csv agree on the qualifying means")
        lx, lc = int(float(dx["losing"])), int(float(dc["losing"]))
        losing_min = min(lx, lc) if losing_min is None else min(losing_min, lx, lc)
        lines.append(
            f"| {q['variant']} | {q['category']} | {label(q['bucket'])} "
            f"| {_fmt(q['exploration_mean_c'], '{:.2f}')} ({_fmt(float(q['exploration_t']), '{:.1f}')}) "
            f"| {_fmt(q['confirmation_mean_c'], '{:.2f}')} ({_fmt(float(q['confirmation_t']), '{:.1f}')}) "
            f"| {_fmt(float(ax['mean_c']), '{:.2f}')}, {_fmt(float(ac['mean_c']), '{:.2f}')} "
            f"| {int(float(dx['clusters']))} ({lx}) / {int(float(dc['clusters']))} ({lc}) |")
        tdiff = (float(dc["mean_c"]) - float(dx["mean_c"])) / math.hypot(float(dx["se_c"]), float(dc["se_c"]))
        changes.append((q, tdiff))
    f.put("km_qual_table", "\n".join(lines), "", cells_path)
    f.put("km_losing_min", losing_min, "{}", cells_path)
    claim(losing_min >= floor_losing, "every qualifying pair meets the losing-cluster floor in each period")

    distinct = sorted({(q["category"], q["side"], q["bucket"]) for q in qual})
    a_sig = sum(
        min(float(cell("A", smp, {"category": ca, "side": si, "bucket": b})["t"]) for smp in ("exploration", "confirmation")) >= 2
        for ca, si, b in distinct)
    f.put("km_cells", len(distinct), "{}", cells_path)
    f.put("km_a_sig", a_sig, "{}", cells_path)
    claim(a_sig >= len(distinct) - 1, "statistic A confirms all but at most one qualifying cell")

    join_only = []
    for ca, si, b in distinct:
        variants = {q["variant"] for q in qual if (q["category"], q["side"], q["bucket"]) == (ca, si, b)}
        q = {"category": ca, "side": si, "bucket": b}
        bx, bc = cell("B", "exploration", q), cell("B", "confirmation", q)
        if variants == {"JOIN"} and max(abs(float(bx["t"])), abs(float(bc["t"]))) < 2:
            join_only.append((ca, bx, bc, cell("C", "exploration", q), cell("C", "confirmation", q)))
    claim(len(join_only) == 1, "exactly one qualifying cell passes on JOIN while PENNY earns nothing")
    ca, bx, bc, cx, cc = join_only[0]
    f.put("km_join_only", ca, "", cells_path)
    f.put("km_join_only_b_x", float(bx["mean_c"]), "{:.2f}", cells_path)
    f.put("km_join_only_b_c", float(bc["mean_c"]), "{:.2f}", cells_path)
    f.put("km_join_only_c_x", float(cx["mean_c"]), "{:.2f}", cells_path)
    f.put("km_join_only_c_c", float(cc["mean_c"]), "{:.2f}", cells_path)
    f.put("km_join_n", sum(q["variant"] == "JOIN" for q in qual), "{}", gate_path)

    f.put("km_decay_n", sum(t < 0 for _, t in changes), "{}", cells_path)
    f.put("km_rise_n", sum(t > 0 for _, t in changes), "{}", cells_path)
    sig = [(q, t) for q, t in changes if abs(t) >= 2]
    claim(len(sig) == 1 and sig[0][1] < 0, "exactly one change between periods is significant on its own, a decline")
    q, t = sig[0]
    f.put("km_sig_change", f"{q['variant']} {q['category']} {label(q['bucket'])}", "", cells_path)
    f.put("km_sig_change_x", q["exploration_mean_c"], "{:.2f}", gate_path)
    f.put("km_sig_change_c", q["confirmation_mean_c"], "{:.2f}", gate_path)
    f.put("km_sig_change_t", t, "{:.1f}", cells_path)

    kalshi_forward(f, gate, sha)

    # exploratory, after the decision: markets settled more than a day after their latest expiration
    sens = read(KALSHI_SENS)
    m = re.search(r"markets in the four categories: \((\d+), (\d+)\)", sens)
    f.put("km_late_universe", int(m.group(1)), "{:,}", KALSHI_SENS)
    f.put("km_late_markets", int(m.group(2)), "{:,}", KALSHI_SENS)
    shares = {}
    for line in sens.splitlines():
        m = re.match(r"(.+?)\s+(short_yes|long_yes)\s+b(\d)\s+contracts.*share\s+([\d.]+)%", line)
        if m:
            shares[(m.group(1).strip(), m.group(2), int(m.group(3)))] = float(m.group(4))
    f.put("km_late_max", max(shares[(q["category"], q["side"], q["bucket"])] for q in qual), "{:.2f} %", KALSHI_SENS)
    # concentration: eligible markets of the qualifying categories (volume.csv) against all eligible markets
    elig_q = sum(int(float(by[smp][cat]["markets"])) for smp in by for cat in cats if cat in by[smp])
    elig_all = c["markets"]
    universe, flagged_q = (int(g) for g in re.search(r"markets in the four categories: \((\d+), (\d+)\)", sens).groups())
    wider = universe - elig_q
    claim(wider >= 0, "the query's universe contains the eligible markets of the qualifying categories")
    late_lo = flagged_q - wider
    f.put("km_late_lo", late_lo, "{:,}", KALSHI_SENS)
    f.put("km_late_lo_share", late_lo / c["markets_settled_after_latest_expiration"] * 100, "{:.0f} %", KALSHI_SENS)
    f.put("km_elig_q_share", elig_q / elig_all * 100, "{:.0f} %", volume_path)
    claim(late_lo / c["markets_settled_after_latest_expiration"] > elig_q / elig_all,
          "late settlement is concentrated in the qualifying categories")

    # exploratory, after the decision: statistic A of the qualifying cells by time to settlement
    hz = read(KALSHI_HORIZON)
    claim("'mve'" in hz.split("--- check")[0], "the horizon query had the multivariate flag available")
    tup = re.compile(r"\('([^']+)', (\d)(?:, '([^']+)')?, (\d+), ([\d.]+), (-?[\d.]+), (-?[\d.]+|None)\)")
    check = hz.split("--- by horizon")[0]
    for mm in tup.finditer(check):
        q = {"category": mm.group(1), "side": "short_yes", "bucket": int(mm.group(2))}
        a = cell("A", "all", q)
        claim(abs(float(a["mean_c"]) - float(mm.group(6))) < 1e-3 and int(float(a["clusters"])) == int(mm.group(4)),
              f"the horizon query reproduces statistic A of {q['category']} in cells.csv")
    pooled = hz.split("--- pooled over the six cells, by horizon")[1]
    rows = {}
    for mm in re.finditer(r"\('([^']+)', (\d+), ([\d.]+), (-?[\d.]+), (-?[\d.]+)\)", pooled):
        rows[mm.group(1)] = (int(mm.group(2)), float(mm.group(3)), float(mm.group(4)), float(mm.group(5)))
    for h, tag in (("1-6h", "h1"), ("6-24h", "h6"), ("24-168h", "h24"), ("168h+", "h168")):
        f.put(f"km_{tag}_mean", rows[h][2], "{:.2f}", KALSHI_HORIZON)
        f.put(f"km_{tag}_t", rows[h][3], "{:.1f}", KALSHI_HORIZON)
        claim(rows[h][2] > 0 and rows[h][3] >= 2, f"statistic A of the qualifying cells is positive with t >= 2 at {h}")
    total = sum(v[1] for v in rows.values())
    f.put("km_short_share", (total - rows["168h+"][1]) / total * 100, "{:.0f} %", KALSHI_HORIZON)
    per, weak = {}, 0
    blk = hz.split("--- by horizon")[1].split("--- pooled")[0]
    for mm in re.finditer(r"\('([^']+)', (\d), '([^']+)', (\d+), ([\d.]+), (-?[\d.]+), (-?[\d.]+|None)\)", blk):
        per.setdefault((mm.group(1), int(mm.group(2))), {})[mm.group(3)] = float(mm.group(5))
        if mm.group(3) != "0-1h" and mm.group(7) != "None" and float(mm.group(7)) < 2:
            weak += 1
    claim(weak > 0, "not every cell earns at every horizon from one hour up")
    short = {k: (sum(v.values()) - v.get("168h+", 0.0)) / sum(v.values()) for k, v in per.items()}
    kmin = min(short, key=short.get)
    f.put("km_short_min", short[kmin] * 100, "{:.0f} %", KALSHI_HORIZON)
    f.put("km_short_min_cell", f"{kmin[0]} {label(kmin[1])}", "", KALSHI_HORIZON)



def kalshi_forward(f: Facts, gate: dict, decision_sha: str) -> None:
    """The forward rule as amended on 25 September (Amendment 4), and where the forward test and
    the holdout stood in the snapshot taken from the server."""
    prereg_path = KALSHI_NOW / "PREREGISTRATION.md"
    prereg = re.sub(r"\s+", " ", read(prereg_path))
    now_sha = hashlib.sha256(prereg_path.read_bytes()).hexdigest()
    f.put("km_prereg_now_sha", now_sha[:16], "", prereg_path)
    gate_now_path = KALSHI_NOW / "gate.json"
    claim(json.loads(read(gate_now_path)) == gate, "the gate has not been rewritten since the decision")

    m = re.search(r"Amendment 4, (\d+ \w+ \d{4}), after the forward test started", prereg)
    f.put("km_amend_date", m.group(1), "", prereg_path)
    claim("It changes the forward test only." in prereg, "the fourth amendment changes the forward test only")
    claim("No look had taken place when this amendment was written" in prereg,
          "no look had taken place when the fourth amendment was written")
    m = re.search(
        r"Success \(Amendment 4\): pooled strategy-view profit per contract > 0 with t >= ([\d.]+) \(clusters "
        r"as in the backtest\), checked at two looks per variant: the first report in which (\d+) events "
        r"have settled and at least (\d+) clusters are negative, if it comes before day (\d+), and the first "
        r"report on or after day (\d+), counting days from the variant's first fill\. A variant that has not "
        r"succeeded at the day-(\d+) look is inconclusive\. A variant is abandoned if its mean is negative in a "
        r"report on or after day (\d+)\.", prereg)
    t_look = float(m.group(1))
    f.put("km_fwd_t", t_look, "{:.2f}", prereg_path)
    f.put("km_fwd_events", int(m.group(2)), "{}", prereg_path)
    f.put("km_fwd_neg", int(m.group(3)), "{}", prereg_path)
    claim(m.group(4) == m.group(5) == m.group(6), "the second look and the end of the test are the same day")
    f.put("km_fwd_final", int(m.group(4)), "{}", prereg_path)
    f.put("km_fwd_days", int(m.group(7)), "{}", prereg_path)
    one_sided = lambda t: 0.5 * math.erfc(t / math.sqrt(2))
    claim(abs(one_sided(t_look) - one_sided(2) / 2) < 5e-4,
          "the threshold of each look is the one-sided error of t >= 2 split in two")
    m = re.search(
        r"a check every day from day (\d+) to day (\d+) gives ([\d.]+) %, .*? The two looks below give "
        r"([\d.]+) % in the same simulation", prereg)
    f.put("km_sim_from", int(m.group(1)), "{}", prereg_path)
    f.put("km_sim_to", int(m.group(2)), "{}", prereg_path)
    f.put("km_sim_daily", float(m.group(3)), "{:.1f} %", prereg_path)
    f.put("km_sim_two", float(m.group(4)), "{:.1f} %", prereg_path)
    claim(float(m.group(4)) < float(m.group(3)), "the two looks give fewer false successes than daily checks")
    m = re.search(r"the forward universe is the (\d+) most active markets closing within (\d+) days", prereg)
    f.put("km_fwd_n", int(m.group(1)), "{}", prereg_path)
    f.put("km_fwd_window", int(m.group(2)), "{}", prereg_path)

    # the forward report, computed on a copy of the paper database by the deployed reporter
    fwd_path = KALSHI_NOW / "reports" / "FORWARD.md"
    fwd = read(fwd_path)
    head = re.search(r"Generated (\S+)T(\d\d:\d\d):\d\d\+00:00\. Pre-registration SHA-256 `([0-9a-f]{64})`; "
                     r"gate of \S+, written under `([0-9a-f]{64})`", fwd)
    claim(head.group(3) == now_sha, "the forward report runs under the amended pre-registration")
    claim(head.group(4) == gate["prereg_sha256"] == decision_sha,
          "the forward report keeps the pre-registration the decision was taken under")
    f.put("km_fwd_time", f"{head.group(1)} {head.group(2)} UTC", "", fwd_path)
    days, fills, events = [], 0, {}
    for variant in ("JOIN", "PENNY"):
        blk = fwd.split(f"## {variant}\n", 1)[1].split("\n## ")[0]
        st = re.search(r"Status: running, day (\d+) of (\d+); look 1 at (\d+) events and (\d+) losing clusters "
                       r"\(now (\d+) and (\d+)\)\.", blk)
        claim(st is not None, f"{variant} is running and has had no look")
        claim(int(st.group(2)) == f.raw["km_fwd_final"] and int(st.group(3)) == f.raw["km_fwd_events"]
              and int(st.group(4)) == f.raw["km_fwd_neg"], f"the {variant} status uses the amended rule")
        days.append(int(st.group(1)))
        events[variant] = (int(st.group(5)), int(st.group(6)))
        mech = md_tables_after(fwd, f"## {variant}")[-1]
        claim(bool(mech) and "via" in mech[0], f"the last {variant} table is the fill mechanics")
        fills += sum(int(num(r["fills"])) for r in mech)
    f.put("km_fwd_day", max(days), "{}", fwd_path)
    f.put("km_fwd_fills", fills, "{:,}", fwd_path)
    f.put("km_fwd_join_events", events["JOIN"][0], "{}", fwd_path)
    f.put("km_fwd_penny_events", events["PENNY"][0], "{}", fwd_path)
    claim(all(n < f.raw["km_fwd_events"] or neg < f.raw["km_fwd_neg"] for n, neg in events.values()),
          "neither variant has reached the minimums of the first look")
    m = re.search(r"^(\d+) cycles; .*?; (\d+) cycles with a failed stage\.$", fwd, re.M)
    f.put("km_fwd_cycles", int(m.group(1)), "{:,}", fwd_path)
    f.put("km_fwd_failed", int(m.group(2)), "{}", fwd_path)

    # which stage failed, and when the holdout's download of market records started
    errs_path = KALSHI_STATUS / "0028-paper-errors-updown-files.log"
    errs = read(errs_path)
    m = re.search(r"^(\d+) cycles with a failed stage\nfirst (\d\d-\d\d) (\d\d:\d\d) last", errs, re.M)
    claim(int(m.group(1)) >= f.raw["km_fwd_failed"], "the error query covers the cycles counted by the report")
    first_fail = (m.group(2), m.group(3))
    kinds = re.findall(r"^(\d+) \| (.+)$", errs.split("--- updown-desk")[0], re.M)
    claim(sum(int(n) for n, _ in kinds) == int(m.group(1)) and all("KalshiError" in k for _, k in kinds),
          "every failed stage is a Kalshi API error")
    snap_path = KALSHI_STATUS / "0027-publish-snapshot.log"
    m = re.search(r"^backtest restarts=\d+ status=running started=\d{4}-(\d\d-\d\d)T(\d\d:\d\d)", read(snap_path), re.M)
    claim(m.groups() <= first_fail, "no stage failed before the holdout started downloading market records")
    f.put("km_holdout_mk_start", m.group(2) + " UTC", "", snap_path)

    hold_path = KALSHI_NOW / "holdout_progress.txt"
    hold = read(hold_path)
    kv = dict(re.findall(r"^(\w+) (\S+)$", hold, re.M))
    claim(kv["hours_done"] == kv["hours_total"], "every holdout hour has been downloaded")
    claim(kv["summary_exists"] == "False", "the holdout has not reported yet")
    f.put("km_holdout_total", int(kv["hours_total"]), "{}", hold_path)
    f.put("km_holdout_trades", int(kv["trades_done"]), "{:,}", hold_path)
    mk = re.findall(r"^\S+ (\d{4}-\d\d-\d\d) (\d\d:\d\d):\S+ INFO kmaker\.ingest: markets: (\d+) of (\d+) fetched", hold, re.M)
    f.put("km_holdout_time", f"{mk[-1][0]} {mk[-1][1]} UTC", "", hold_path)
    f.put("km_holdout_mk_done", int(mk[-1][2]), "{:,}", hold_path)
    f.put("km_holdout_mk_total", int(mk[-1][3]), "{:,}", hold_path)


def build_facts() -> Facts:
    f = Facts()
    for step in (updown, updown_readme, passive, backtest, xarb, kalshi):
        step(f)
    return f
