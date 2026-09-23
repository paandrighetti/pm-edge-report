# Prediction-market research: one-page summary

Five studies on Polymarket and Kalshi public data, September 2026. Three decide with a rule
stated before the statistic it governs; the other two are measurements. Full report:
[REPORT.md](REPORT.md).

- **Settlement.** Polymarket's 15-minute crypto markets settle on a 60-second Chainlink
  average: it agrees with 100.0 % of 2,680 outcomes in the latest week
  (98.8 % over the first six days), against 93.9 % for Binance. A spot-priced fair value prices the wrong contract.
- **Taking.** A TWAP-aware fair value roughly matches the market mid in accuracy and loses in
  all 12 cells of a taker grid (t from -3.4 to -1.8) once
  spread, fees and latency apply.
- **Resolved markets.** On 84,160 markets, favorites are overpriced rather than cheap
  at the last hourly print (favorite carry loses 0.8 % per trade out of sample,
  t = -6.5); the best hedge cell (t = 4.1) reverses (t = -2.4); a Dutch-book
  residual survives only in a few cheap books, unsized.
- **Market making.** On 1,512,913 prints, resting liquidity earns about the maker rebate in
  one price bucket; fills that reach the back of the queue lose 0.56 and
  0.35 cents per share before it.
- **Cross-venue arbitrage.** Exact Kalshi and Polymarket pairs show 0.6 cents of
  entry edge, sound at settlement but hard to fill (median episode a single poll); pairs
  settling on different sources or at different instants show more edge (1.9 cents) and a negative result
  (-7.2 cents per contract, 2 divergent settlements).
- **Kalshi maker premium.** Pending: the pre-registered backtest has not written its decision yet.

Tools: Python, DuckDB, Docker on a self-hosted server, public REST and websocket APIs,
cluster-robust inference, reproducible reports generated from raw outputs.
