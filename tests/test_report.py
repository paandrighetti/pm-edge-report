import re
import subprocess
import sys

from pmedge.build import TEMPLATES, build, main
from pmedge.facts import ROOT, _fmt
from pmedge.tables import fixed_width, md_table, num

# Digits allowed in template prose: fixed descriptions of the contracts and buckets, years,
# section numbers and bibliographic references. Every measured figure must be a placeholder.
ALLOWED = [
    r"^\s*0\.5,",
    r"\b(?:19|20)\d\d\b", r"^\s*(\d+\.|##\s*\d+\.)", r"15-minute", r"60-second", r"30-second",
    r"\b10 minutes\b", r"\b14 minutes\b", r"\b5 minutes\b", r"0\.1 to 0\.3", r"from 0\.5",
    r"\bSSRN \d+", r"Paper \d+", r"\d+\(\d+\), \d+-\d+", r"90th", r"one tick", r"SHA-256",
    r"\bsum(?:ming)? away from one\b", r"MANIFEST\.sha256", r"t below -2",
    r"0\.21 to 0\.39 and 0\.61 to 0\.79", r"t ≥ 2",
]


def test_build_is_current():
    assert main(["--check"]) == 0


def test_template_prose_has_no_hand_typed_figures():
    for path in TEMPLATES.glob("*.md"):
        body = path.read_text(encoding="utf-8")
        body = body.split("## References")[0]
        for line in body.splitlines():
            stripped = re.sub(r"\{[a-z0-9_]+\}", "", line)
            for pat in ALLOWED:
                stripped = re.sub(pat, "", stripped)
            stripped = re.sub(r"https?://\S+", "", stripped)
            assert not re.search(r"\d", stripped), f"{path.name}: hand-typed figure in: {line}"


def test_every_placeholder_resolves():
    report = build()["REPORT.md"]
    assert not re.search(r"\{[a-z0-9_]+\}", report)


def test_no_em_dash():
    for text in build().values():
        assert "—" not in text


def test_manifest_matches_snapshot():
    for manifest in (ROOT / "sources").glob("*/MANIFEST.sha256"):
        r = subprocess.run(["sha256sum", "-c", "--quiet", manifest.name], cwd=manifest.parent)
        assert r.returncode == 0


def test_half_up_rounding():
    assert _fmt(0.245, "{:+.2f}") == "+0.25"
    assert _fmt(-0.0001, "{:.1f}") == "0.0"
    assert _fmt(97.35000000000001, "{:.1f} %") == "97.4 %"


def test_parsers():
    md = "## T\n\n| a | b |\n|---|---|\n| 1,000 | x y |\n"
    assert md_table(md, "## T") == [{"a": "1,000", "b": "x y"}]
    assert num("1,000") == 1000.0
    lines = ["family   bucket      t", " tau_s  [0, 60)  -0.77", "note = free text"]
    assert fixed_width(lines) == [{"family": "tau_s", "bucket": "[0, 60)", "t": "-0.77"}]
