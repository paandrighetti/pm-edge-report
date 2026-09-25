#!/usr/bin/env bash
# Read-only: what pm-edge-report needs to describe the Kalshi study as of now (amended
# pre-registration, a forward report computed on a copy of the paper database, holdout
# progress), and the deployed versions of updown-desk and pm-xarb, to compare with their
# repositories before they are made public. Nothing under /opt is written.
set -uo pipefail
K=/opt/kalshi-maker
ts=$(date -u +%Y%m%dT%H%MZ)
dst="$GITHUB_WORKSPACE/results/sources/kalshi-$ts"
mkdir -p "$dst/reports"
echo "--- kalshi-maker deployed version"
git -c safe.directory=$K -C $K log --oneline -3
cp "$K/PREREGISTRATION.md" "$K/data/gate.json" "$dst/"
cp "$K/reports/BACKTEST.md" "$dst/reports/"
cp "$K/reports/FORWARD.md" "$dst/reports/FORWARD-last-daily.md" 2>/dev/null || echo "no FORWARD.md"
cp "$K/data/forward_status.json" "$dst/" 2>/dev/null || echo "no forward_status.json yet"
cp "$K/data/manifest_r1.json" "$dst/" 2>/dev/null || echo "no manifest_r1.json yet"

echo "--- forward report on a copy of the paper database (reporter image, Amendment 4 code)"
docker exec -i kalshi-maker-reporter-1 python - > "$dst/reports/FORWARD.md" <<'PY'
import os, shutil, sqlite3, tempfile
from pathlib import Path
from kmaker import report
src = Path(os.environ.get("KM_DATA_DIR", "/data"))
tmp = Path(tempfile.mkdtemp())
s = sqlite3.connect(f"file:{src / 'paper.sqlite'}?mode=ro", uri=True)
d = sqlite3.connect(tmp / "paper.sqlite")
s.backup(d)
d.close(); s.close()
for name in ("gate.json", "forward_status.json"):
    if (src / name).exists():
        shutil.copy(src / name, tmp / name)
text, digest = report.forward_report(tmp)
print(text, end="")
print("\n<!-- digest\n" + digest + "\n-->")
PY
cat "$dst/reports/FORWARD.md"

echo "--- holdout progress"
docker exec -i kalshi-maker-reporter-1 python - > "$dst/holdout_progress.txt" <<'PY'
import os
from datetime import datetime, timezone
from pathlib import Path
from kmaker.config import PREREG
from kmaker.ingest import hour_counts, sampled_hours
d = Path(os.environ.get("KM_DATA_DIR", "/data"))
r = PREREG.holdout_residue
hours = sampled_hours(PREREG.window_start, PREREG.window_end, PREREG.hour_mod, r)
done = hour_counts(d, r)
print(f"checked_at {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC")
print(f"holdout_residue {r}")
print(f"hours_total {len(hours)}")
print(f"hours_done {len(done)}")
print(f"trades_done {sum(done.values())}")
print(f"summary_exists {(Path(os.environ.get('KM_REPORTS_DIR', '/reports')) / 'backtest' / f'r{r}' / 'summary.json').exists()}")
PY
docker logs --timestamps --since 30h kalshi-maker-backtest-1 2>&1 | grep -E "trades r1 complete|markets: " | tail -4 >> "$dst/holdout_progress.txt"
cat "$dst/holdout_progress.txt"
docker inspect kalshi-maker-backtest-1 --format 'backtest restarts={{.RestartCount}} status={{.State.Status}} started={{.State.StartedAt}}'

(cd "$dst" && find . -type f ! -name MANIFEST.sha256 -print0 | sort -z | xargs -0 sha256sum > MANIFEST.sha256)

echo "--- updown-desk deployed version"
U=/opt/updown-desk
git -c safe.directory=$U -C $U log --oneline -4 2>&1
git -c safe.directory=$U -C $U status --short 2>&1 | head -10

echo "--- pm-xarb deployed files"
X=/opt/pm-xarb
(cd $X && find src config config.yaml README.md pyproject.toml Dockerfile docker-compose.yml deploy tests -type f ! -path '*__pycache__*' -print0 2>/dev/null | sort -z | xargs -0 sha256sum)
git -c safe.directory=$X -C $X log --oneline -2 2>&1 | head -2
exit 0
