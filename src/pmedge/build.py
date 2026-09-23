"""Render REPORT.md from templates/ and the facts read from sources/.

    python -m pmedge.build           write REPORT.md and facts.json
    python -m pmedge.build --check   fail if either is out of date
"""
from __future__ import annotations

import json
import re
import sys

from .facts import ROOT, build_facts

TEMPLATES = ROOT / "templates"
PLACEHOLDER = re.compile(r"\{([a-z0-9_]+)\}")


def derived(values: dict[str, str], raw: dict) -> dict[str, str]:
    """Sentences whose wording depends on the data, chosen here and nowhere else."""
    out = {}
    if raw["km_status"] == "pending":
        out["km_verdict"] = "Pending: the pre-registered backtest has not written its decision yet."
        out["km_section"] = (TEMPLATES / "kalshi_pending.md").read_text(encoding="utf-8").strip()
    else:
        raise NotImplementedError("gate.json exists: write templates/kalshi_decided.md from its fields")
    out["pm_xarb_exact_verdict"] = (
        f"edges of about {values['xa_exact_edge_mean']} that rarely outlast a poll; sound at settlement, "
        "lost in execution so far."
    )
    return out


def render(template: str, values: dict[str, str]) -> str:
    missing = sorted({k for k in PLACEHOLDER.findall(template) if k not in values})
    if missing:
        raise KeyError(f"no fact for: {', '.join(missing)}")
    text = template
    # nested placeholders (a section that contains placeholders) resolve in two passes
    for _ in range(2):
        text = PLACEHOLDER.sub(lambda m: values[m.group(1)], text)
    return text


def build() -> dict[str, str]:
    f = build_facts()
    values = dict(f.values)
    values.update(derived(values, f.raw))
    report = render((TEMPLATES / "REPORT.md").read_text(encoding="utf-8"), values)
    summary = render((TEMPLATES / "SUMMARY.md").read_text(encoding="utf-8"), values)
    facts = json.dumps(
        {k: {"value": f.raw[k], "printed": f.values[k], "source": f.source[k]} for k in f.values},
        indent=1, ensure_ascii=False,
    ) + "\n"
    return {"REPORT.md": report, "SUMMARY.md": summary, "facts.json": facts}


def main(argv: list[str]) -> int:
    outputs = build()
    if "--check" in argv:
        stale = [n for n, t in outputs.items()
                 if not (ROOT / n).exists() or (ROOT / n).read_text(encoding="utf-8") != t]
        if stale:
            print("out of date: " + ", ".join(stale) + " (run python -m pmedge.build)")
            return 1
        print("up to date")
        return 0
    for name, text in outputs.items():
        (ROOT / name).write_text(text, encoding="utf-8")
        print(f"wrote {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
