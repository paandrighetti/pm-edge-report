# Prediction-market research: one-page summary

Five studies on Polymarket and Kalshi public data, September 2026. Four decide with a rule
written before the data that decides it; the fifth is a cross-venue measurement desk. Full
report: [REPORT.md](REPORT.md).

- **Settlement.** Polymarket's 15-minute crypto markets settle on a 60-second Chainlink
  average: it agrees with 100.0 % of 2,680 outcomes, against 93.9 %
  for Binance. A spot-priced fair value prices the wrong contract.
- **Taking.** A TWAP-aware fair value beats the market mid late in the window but loses in all
  12 cells of a taker grid (t from -3.4 to -1.8) once
  spread, fees and latency apply.
- **Resolved markets.** On 84,160 markets, favorites are overpriced rather than cheap
  (favorite carry loses 0.8 % per trade out of sample, t = -6.5); the only in-sample
  winner (t = 4.1) reverses out of sample (t = -2.4).
- **Market making.** On 1,512,913 prints, resting liquidity earns about the maker rebate in
  one price bucket; fills that reach the back of the queue lose 0.56 and
  0.35 cents per share before it.
- **Cross-venue arbitrage.** Exact Kalshi and Polymarket pairs show 0.6 cents of
  edge that vanishes within a poll; pairs settling on different sources show more edge
  (1.9 cents) and a negative result (-7.2 cents per contract).
- **Kalshi maker premium.** Pending: the pre-registered backtest is downloading its sample.

Tools: Python, DuckDB, Docker on a self-hosted server, public REST and websocket APIs,
cluster-robust inference, reproducible reports generated from raw outputs.
