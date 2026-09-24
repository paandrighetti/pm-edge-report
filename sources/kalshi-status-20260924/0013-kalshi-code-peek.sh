#!/usr/bin/env bash
# Read-only: schema and SQL used by the backtest, to run a sensitivity query next; paper fills so far.
set -uo pipefail
K=/opt/kalshi-maker/src/kmaker
grep -n -A12 "MARKET_COLUMNS\s*=" $K/ingest.py | head -30
grep -n -A10 "TRADE_COLUMNS\s*=\|SCHEMA\s*=" $K/*.py | head -30
echo "--- settled_after_latest_expiration and period split in backtest.py"
grep -n -B8 -A8 "settled_after_latest_expiration\|latest_expiration" $K/backtest.py | head -120
echo "--- paper fills by variant and category"
docker exec -i kalshi-maker-paper-1 python - <<'PY'
import sqlite3, os
p = os.path.join(os.environ.get("KM_DATA_DIR", "/data"), "paper.sqlite")
con = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
for row in con.execute("select variant, category, side, bucket, count(*), sum(qty), round(avg(price),3) from fills group by 1,2,3,4 order by 5 desc"):
    print(row)
print(con.execute("select min(ts_us), max(ts_us) from fills").fetchone())
print(con.execute("select count(*), avg(active), avg(candidates), avg(orders), sum(fills), sum(errors), avg(duration_s) from cycles").fetchone())
PY
exit 0
