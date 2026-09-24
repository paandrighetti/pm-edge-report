#!/usr/bin/env bash
# Read-only: snapshots the kalshi-maker decision and reports the holdout and paper status.
set -uo pipefail
K=/opt/kalshi-maker
dst="$GITHUB_WORKSPACE/results/sources/kalshi-$(date -u +%Y%m%dT%H%MZ)"
mkdir -p "$dst"
cp "$K/data/gate.json" "$dst/" 2>/dev/null || echo "no gate.json"
cp "$K/PREREGISTRATION.md" "$dst/"
cp -r "$K/reports/." "$dst/reports/" 2>/dev/null
rm -f "$dst/reports/.gitkeep"
(cd "$dst" && find . -type f ! -name MANIFEST.sha256 -print0 | sort -z | xargs -0 sha256sum > MANIFEST.sha256)
echo "--- snapshot"; (cd "$dst" && find . -type f -printf '%8s %p\n' | sort -k2)
echo "--- digest order (exploration / confirmation?)"
grep -n -A25 "def _gate_digest" "$K/src/kmaker/cli.py" | head -40
echo "--- backtest log (last 25)"
docker logs --tail 25 kalshi-maker-backtest-1 2>&1
echo "--- paper log (last 25)"
docker logs --tail 25 kalshi-maker-paper-1 2>&1
echo "--- paper.sqlite (read-only)"
docker exec -i kalshi-maker-paper-1 python - <<'PY'
import sqlite3, os
p = os.path.join(os.environ.get("KM_DATA_DIR", "/data"), "paper.sqlite")
if not os.path.exists(p):
    print("no paper.sqlite yet"); raise SystemExit
con = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
for (t,) in con.execute("select name from sqlite_master where type='table' order by name"):
    n = con.execute(f"select count(*) from {t}").fetchone()[0]
    cols = [r[1] for r in con.execute(f"pragma table_info({t})")]
    print(f"{t}: {n} rows; columns {cols}")
PY
exit 0
