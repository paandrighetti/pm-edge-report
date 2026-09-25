#!/usr/bin/env bash
# Read-only: which stage failed in the paper maker's 63 cycles since this morning, and the
# checksums of updown-desk's deployed files, to compare with the public commit b4c0c95.
set -uo pipefail
echo "--- paper maker: failed stages"
docker exec -i kalshi-maker-paper-1 python - <<'PY'
import os, sqlite3
from datetime import datetime, timezone
p = os.path.join(os.environ.get("KM_DATA_DIR", "/data"), "paper.sqlite")
con = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
fmt = lambda us: datetime.fromtimestamp(us / 1e6, timezone.utc).strftime("%m-%d %H:%M")
rows = con.execute("select ts_us, errors from cycles where errors is not null and errors != '' order by ts_us").fetchall()
print(len(rows), "cycles with a failed stage")
if rows:
    print("first", fmt(rows[0][0]), "last", fmt(rows[-1][0]))
    kinds = {}
    for _, e in rows:
        k = e[:160]
        kinds[k] = kinds.get(k, 0) + 1
    for k, n in sorted(kinds.items(), key=lambda x: -x[1])[:8]:
        print(n, "|", k)
    by_hour = {}
    for ts, _ in rows:
        h = fmt(ts)[:8]
        by_hour[h] = by_hour.get(h, 0) + 1
    print("by hour:", by_hour)
PY
echo "--- updown-desk deployed files"
cd /opt/updown-desk && find README.md pyproject.toml src docs scripts tests -type f ! -path '*__pycache__*' -print0 2>/dev/null | sort -z | xargs -0 sha256sum
exit 0
