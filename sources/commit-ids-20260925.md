# Commit ids before and after 25 September 2026

On 25 September 2026 the author and committer of every commit of updown-desk, pm-backtest,
kalshi-maker, pm-xarb and this repository were set to the repository owner. Messages, trees,
dates and file contents are unchanged; only the commit ids changed. The server logs in
`sources/` quote the ids of the time. Two source folders are named after a commit and were
renamed: `updown-desk-b4c0c95` to `updown-desk-547d806` and `pm-backtest-86fa1aa` to
`pm-backtest-c8c343a`. kalshi-maker lists its own ids in its `history-rewrite.md`.

## updown-desk

| old | new | commit |
|---|---|---|
| 31896ce | fcbad44 | initial |
| 6a263f4 | 6bd397b | collector: compress raw files every 30 min, quieter http logs |
| c270e17 | 043a548 | collector: unfiltered binance feed, drop-events lever, lf line endings |
| 4c09171 | a39aecf | derived parquet layer, memory caps, empty-vol fix |
| 994c472 | 67f1ea4 | add pyarrow dependency |
| f6c44ba | cbade56 | receive watchdog and protocol pings, single compressor |
| 843cd32 | d9bdffd | books extraction inside duckdb, per-file coverage |
| f8bd96f | 96dbe5b | gamma outcome sweep, memory-bounded report |
| 9e329a2 | 1735bf7 | restore pyarrow dependency |
| a56d42b | c17932b | memory-bounded report: arrow categoricals, duckdb agreement, numpy replay |
| 476b142 | d71eedd | twap settlement model, spot and reference feeds, findings in readme |
| 14df763 | 5ab1c29 | daily report in a worker thread, rolling seven-day window, memory headroom |
| ac0ee25 | 22e169f | 0.2.0: passive quoting replay, pre-registered 21 September 2026 |
| b4c0c95 | 547d806 | 0.3.0: close the passive quoting study |

## pm-backtest

| old | new | commit |
|---|---|---|
| f3f61b6 | 97eaabb | initial: walk-forward backtests on 84k resolved Polymarket markets |
| f1cfd9b | cc46052 | remove pre-ingestion reports and duplicate script, lf line endings |
| 86fa1aa | c8c343a | validity table counts each book once, readme reading by side |
