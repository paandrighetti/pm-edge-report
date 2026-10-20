# pm-edge-report

Where does a small, slow participant find an edge on prediction markets, and where does it not?
This repository synthesises five studies run on public Polymarket and Kalshi data in September and
October 2026: which price a market settles on, what a taker earns against a fair value, three
classic strategies on resolved markets, what resting liquidity earns, cross-venue arbitrage, and the
maker premium on Kalshi.

- [SUMMARY.md](SUMMARY.md): one page.
- [REPORT.md](REPORT.md): the full report, with methods, results, limitations and references.

## The studies

| Report section | Question | Code | Status |
|---|---|---|---|
| 1. Settlement | Which feed does a 15-minute Up/Down market resolve on? | [updown-desk](https://github.com/paandrighetti/updown-desk) | closed |
| 2. Taking against a fair value | Does a model-based taker beat the market after spread, fees and latency? | [updown-desk](https://github.com/paandrighetti/updown-desk) | closed |
| 3. Resolved markets | Favorite carry, Dutch books and hedged binaries, walk-forward | [pm-backtest](https://github.com/paandrighetti/pm-backtest) | closed |
| 4. Providing liquidity | What do resting orders earn on the tape? | [updown-desk](https://github.com/paandrighetti/updown-desk) | closed |
| 5. Cross-venue arbitrage | How much of a Kalshi and Polymarket price gap can a taker capture? | [pm-xarb](https://github.com/paandrighetti/pm-xarb) | closed |
| 6. Kalshi maker premium | Does a slow maker at the back of the queue earn the retail-flow premium? | [kalshi-maker](https://github.com/paandrighetti/kalshi-maker) | forward paper test running |

Each study states what it decides and when. The Kalshi study was pre-registered before any of its
data was downloaded, and its forward test has two fixed looks with a corrected threshold.

## How the figures are produced

No figure in REPORT.md or SUMMARY.md is typed by hand.

1. `sources/` holds the outputs copied from each study: reports, decision files and logs. Outputs
   produced on the server come with a `MANIFEST.sha256`.
2. `src/pmedge/facts.py` reads every printed figure from those files. Each statement the text makes
   about a sign, a significance or "every cell" is checked against the data; if a source no longer
   supports it, the build fails.
3. `templates/` holds the prose, with a placeholder for each figure. A test fails if a template
   contains a measured figure.
4. `facts.json` lists every printed figure with its raw value and the file it came from.

## Reproduce

```
pip install -e ".[dev]"
python -m pmedge.build      # regenerate REPORT.md, SUMMARY.md and facts.json
pytest -q                   # fails if they are out of date, if a claim no longer holds or if a checksum differs
```

## Layout

```
sources/            outputs copied from the studies, with checksums
src/pmedge/         facts.py (figures and checked claims), tables.py (parsers), build.py (rendering)
templates/          the prose of REPORT.md and SUMMARY.md
tests/              build up to date, no hand-typed figure, every placeholder resolved, checksums
```

## License

The code is under the MIT License ([LICENSE-CODE.md](LICENSE-CODE.md)). The text of the report and
of the summary is under the Creative Commons Attribution 4.0 International License
([LICENSE-CONTENT.md](LICENSE-CONTENT.md)).

## Disclaimer

Research on public market data. Every fill is simulated and no order was ever placed. This is not
investment advice.
