#!/usr/bin/env bash
# Read-only exploratory check: statistic A of the qualifying cells by time to settlement,
# to compare with the forward test universe (markets closing within 7 days).
set -uo pipefail
docker exec -i kalshi-maker-backtest-1 python - <<'PY'
import os, shutil
from datetime import datetime, timezone
import duckdb
tmp = "/data/tmp_horizon"
os.makedirs(tmp, exist_ok=True)
con = duckdb.connect()
con.execute("SET memory_limit='400MB'"); con.execute("SET threads=2")
con.execute(f"SET temp_directory='{tmp}'")
cols = [r[0] for r in con.execute("DESCRIBE SELECT * FROM read_parquet('/data/markets/*.parquet')").fetchall()]
print("market columns:", cols)
mve = "arg_max(m.mve, m.filename)" if "mve" in cols else "FALSE"
cutoff = int(datetime(2026, 9, 15, tzinfo=timezone.utc).timestamp() * 1e6)
split = int(datetime(2026, 5, 1, tzinfo=timezone.utc).timestamp() * 1e6)
cells = "(('Entertainment',0),('Entertainment',1),('Mentions',1),('Mentions',2),('Politics',0),('Climate and Weather',0))"
con.execute(f"""
CREATE TEMP TABLE mk AS
SELECT m.ticker,
       arg_max(m.latest_expiration_us, m.filename) AS lexp,
       arg_max(m.settlement_us, m.filename) AS sett,
       arg_max(m.status, m.filename) AS status,
       arg_max(m.result, m.filename) AS result,
       {mve} AS mve,
       arg_max(s.category, m.filename) AS cat,
       arg_max(s.fee_type, m.filename) AS fee_type,
       arg_max(coalesce(s.fee_multiplier, 1.0), m.filename) AS mult
FROM read_parquet('/data/markets/*.parquet', filename=true) m
JOIN read_parquet('/data/series.parquet') s ON s.series = m.series
WHERE s.category IN ('Entertainment','Mentions','Politics','Climate and Weather')
  AND m.ticker NOT LIKE 'KXMVE%'
GROUP BY m.ticker
""")
con.execute(f"""
CREATE TEMP TABLE x AS
SELECT mk.cat,
       CASE WHEN t.yes_price < 0.10 THEN 0 WHEN t.yes_price < 0.30 THEN 1
            WHEN t.yes_price < 0.70 THEN 2 WHEN t.yes_price < 0.90 THEN 3 ELSE 4 END AS b,
       CASE WHEN (mk.sett - t.created_us) < 3.6e9 THEN '0-1h'
            WHEN (mk.sett - t.created_us) < 6*3.6e9 THEN '1-6h'
            WHEN (mk.sett - t.created_us) < 24*3.6e9 THEN '6-24h'
            WHEN (mk.sett - t.created_us) < 168*3.6e9 THEN '24-168h'
            ELSE '168h+' END AS h,
       CASE WHEN mk.lexp < {split} THEN 'exploration' ELSE 'confirmation' END AS period,
       mk.cat || ':' || CAST(floor(mk.sett / 86400e6) AS BIGINT) AS cl,
       t.count AS w,
       100 * (t.yes_price - CASE WHEN mk.result = 'yes' THEN 1.0 ELSE 0.0 END)
         - CASE WHEN mk.fee_type = 'quadratic_with_maker_fees'
                THEN 100 * 0.0175 * mk.mult * t.yes_price * (1 - t.yes_price) ELSE 0 END AS v
FROM read_parquet('/data/trades_r0/*.parquet') t JOIN mk USING (ticker)
WHERE t.taker_yes AND NOT t.is_block AND NOT mk.mve
  AND mk.lexp <= {cutoff} AND mk.status IN ('finalized','settled') AND mk.result IN ('yes','no')
""")
con.execute(f"DELETE FROM x WHERE (cat, b) NOT IN {cells}")
def table(keys):
    k = ", ".join(keys)
    return con.execute(f"""
    WITH m AS (SELECT {k}, sum(w*v)/sum(w) AS mean, sum(w) AS sw FROM x GROUP BY {k}),
    g AS (SELECT {', '.join('x.'+c for c in keys)}, x.cl, sum(x.w*(x.v - m.mean)) AS e
          FROM x JOIN m USING ({k}) GROUP BY {', '.join('x.'+c for c in keys)}, x.cl),
    a AS (SELECT {k}, count(*) AS G, sum(e*e) AS ss FROM g GROUP BY {k})
    SELECT {k}, a.G, round(m.sw), m.mean,
           CASE WHEN a.G > 1 THEN m.mean / (sqrt(a.G/(a.G-1.0)*a.ss)/m.sw) END AS t
    FROM m JOIN a USING ({k}) ORDER BY {k}
    """).fetchall()
print("--- check against cells.csv, statistic A, all horizons: cat, bucket, clusters, contracts, mean_c, t")
for r in table(["cat", "b"]): print(r)
print("--- by horizon: cat, bucket, horizon, clusters, contracts, mean_c, t")
for r in table(["cat", "b", "h"]): print(r)
print("--- pooled over the six cells, by horizon")
for r in table(["h"]): print(r)
con.close()
shutil.rmtree(tmp, ignore_errors=True)
PY
exit 0
