#!/usr/bin/env bash
# Read-only sensitivity: share of contracts, in the qualifying categories, traded in markets that
# settled more than a day after their latest_expiration_time (a possibly moved field).
set -uo pipefail
grep -n -i "bucket" /opt/kalshi-maker/src/kmaker/backtest.py | head -20
grep -n -i "BUCKET\|split\|cutoff" /opt/kalshi-maker/src/kmaker/config.py | head -20
docker exec -i kalshi-maker-backtest-1 python - <<'PY'
import os, shutil
from datetime import datetime, timezone
import duckdb
tmp = "/data/tmp_sensitivity"
os.makedirs(tmp, exist_ok=True)
con = duckdb.connect()
con.execute("SET memory_limit='400MB'"); con.execute("SET threads=2")
con.execute(f"SET temp_directory='{tmp}'")
print(con.execute("DESCRIBE SELECT * FROM read_parquet('/data/series.parquet')").fetchall())
cutoff = int(datetime(2026, 9, 15, tzinfo=timezone.utc).timestamp() * 1e6)
cats = "('Entertainment','Mentions','Politics','Climate and Weather')"
con.execute(f"""
CREATE TEMP TABLE mk AS
SELECT m.ticker,
       arg_max(m.latest_expiration_us, m.filename) AS lexp,
       arg_max(m.settlement_us, m.filename) AS sett,
       arg_max(s.category, m.filename) AS category
FROM read_parquet('/data/markets/*.parquet', filename=true) m
JOIN (SELECT series, category FROM read_parquet('/data/series.parquet') WHERE category IN {cats}) s
  ON s.series = m.series
WHERE m.ticker NOT LIKE 'KXMVE%'
GROUP BY m.ticker
""")
print("markets in the four categories:", con.execute("SELECT count(*), sum((sett > lexp + 86400e6)::INT) FROM mk WHERE lexp <= ?", [cutoff]).fetchone())
rows = con.execute(f"""
SELECT category,
       CASE WHEN t.taker_yes THEN 'short_yes' ELSE 'long_yes' END AS side,
       CASE WHEN t.yes_price < 0.10 THEN 0 WHEN t.yes_price < 0.30 THEN 1
            WHEN t.yes_price < 0.70 THEN 2 WHEN t.yes_price < 0.90 THEN 3 ELSE 4 END AS bucket,
       round(sum(t.count)) AS contracts,
       round(sum(CASE WHEN mk.sett > mk.lexp + 86400e6 THEN t.count ELSE 0 END)) AS late
FROM read_parquet('/data/trades_r0/*.parquet') t JOIN mk USING (ticker)
WHERE mk.lexp <= {cutoff} AND NOT t.is_block
GROUP BY 1, 2, 3 ORDER BY 1, 2, 3
""").fetchall()
for r in rows:
    share = r[4] / r[3] if r[3] else 0
    print(f"{r[0]:20} {r[1]:9} b{r[2]} contracts {r[3]:>14,.0f} late {r[4]:>12,.0f} share {share:6.2%}")
con.close()
shutil.rmtree(tmp, ignore_errors=True)
PY
exit 0
