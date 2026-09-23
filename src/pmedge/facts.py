"""Every figure the report prints, read from the source outputs.

Each fact records the file it came from. Statements the report makes in words (a sign, a
significance, "every cell") are checked here with `claim`; if a regenerated source
contradicts one, the build fails instead of printing a sentence the data no longer supports.
"""
from __future__ import annotations

import hashlib
import json
import re
from decimal import ROUND_HALF_UP, Decimal
from dataclasses import dataclass, field
from pathlib import Path

from .tables import fixed_width, md_table, num, read, text_section

ROOT = Path(__file__).resolve().parents[2]
SERVER = ROOT / "sources" / "server-20260923T2149Z"
BACKTEST = ROOT / "sources" / "pm-backtest-86fa1aa" / "2026-09-18.md"


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
    f.put("ud_taker_trades", sum(int(num(r["n"])) for r in grid if r["latency_ms"] == "0"), "{:,}", src)
    f.put("ud_fee_share_lo", min(fee_share) * 100, "{:.0f} %", src)
    f.put("ud_fee_share_hi", max(fee_share) * 100, "{:.0f} %", src)

    brier = {int(num(r["offset_s"])): r for r in md_table(text, "## Model versus market at fixed checkpoints")}
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
    claim(num(se["pnl"]) < 0, "exact pairs lose since inception")

    cf = {r["klass"]: r for r in md_table(text, "## Classes not traded: counterfactual")}
    b = cf["basis"]
    f.put("xa_basis_cf_pairs", int(num(b["pairs"])), "{}", src)
    f.put("xa_basis_div", int(num(b["divergent"])), "{}", src)
    f.put("xa_basis_edge", num(b["mean_edge_at_entry"]) * 100, "{:.1f} cents", src)
    f.put("xa_basis_pnl", num(b["mean_pnl_per_contract"]) * 100, "{:.1f} cents", src)
    claim(num(b["mean_edge_at_entry"]) > wmean, "basis pairs show more entry edge than exact pairs")
    claim(num(b["mean_edge_at_entry"]) > 0 > num(b["mean_pnl_per_contract"]),
          "basis pairs show a positive entry edge and a negative result")


# --------------------------------------------------------------------------- kalshi-maker
def kalshi(f: Facts) -> None:
    src = SERVER / "kalshi-maker" / "PREREGISTRATION.md"
    f.put("km_prereg_sha", hashlib.sha256(src.read_bytes()).hexdigest()[:16], "", src)
    gate = SERVER / "kalshi-maker" / "gate.json"
    if gate.exists():
        g = json.loads(read(gate))
        f.put("km_status", "decided", "", gate)
        f.put("km_gate", json.dumps(g)[:400], "", gate)
    else:
        f.put("km_status", "pending", "", src)


def build_facts() -> Facts:
    f = Facts()
    for step in (updown, passive, backtest, xarb, kalshi):
        step(f)
    return f
