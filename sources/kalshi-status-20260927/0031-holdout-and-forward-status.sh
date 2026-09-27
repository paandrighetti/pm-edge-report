#!/usr/bin/env bash
# Read-only: did the holdout finish, and with what result; today's forward report; when the
# paper maker's API errors stopped. Copies the outputs to results/sources for the repositories.
set -uo pipefail
K=/opt/kalshi-maker
ts=$(date -u +%Y%m%dT%H%MZ)
dst="$GITHUB_WORKSPACE/results/sources/kalshi-$ts"
mkdir -p "$dst/reports/backtest"
echo "--- backtest container and log tail"
docker ps --format '{{.Names}} {{.Status}}' | grep kalshi
docker logs --timestamps --tail 15 kalshi-maker-backtest-1 2>&1 | cut -c1-220
echo "--- holdout outputs"
ls -la "$K/reports/backtest/" "$K/reports/backtest/r1" 2>&1 | head -20
cp "$K/PREREGISTRATION.md" "$K/data/gate.json" "$dst/"
cp "$K/reports/BACKTEST.md" "$K/reports/FORWARD.md" "$dst/reports/"
cp -r "$K/reports/backtest/r1" "$dst/reports/backtest/" 2>/dev/null || echo "no r1 outputs"
cp "$K/data/forward_status.json" "$dst/" 2>/dev/null || echo "no forward_status.json"
cp "$K/data/manifest_r1.json" "$dst/" 2>/dev/null || echo "no manifest_r1.json"
(cd "$dst" && find . -type f ! -name MANIFEST.sha256 -print0 | sort -z | xargs -0 sha256sum > MANIFEST.sha256)
echo "--- holdout section of BACKTEST.md"
sed -n '/## Holdout hours/,$p' "$K/reports/BACKTEST.md" | head -20
echo "--- git status of the server copy"
git -c safe.directory=$K -C $K status --short | head
echo "--- today's forward report"
cat "$K/reports/FORWARD.md"
echo "--- paper maker: last failed stage"
docker exec -i kalshi-maker-paper-1 python - <<'PY'
import os, sqlite3
from datetime import datetime, timezone
p = os.path.join(os.environ.get("KM_DATA_DIR", "/data"), "paper.sqlite")
con = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
fmt = lambda us: datetime.fromtimestamp(us / 1e6, timezone.utc).strftime("%Y-%m-%d %H:%M")
r = con.execute("select count(*), max(ts_us) from cycles where errors is not null and errors != ''").fetchone()
print("failed cycles total", r[0], "last", fmt(r[1]) if r[1] else None)
PY
exit 0
