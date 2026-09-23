# Prediction-market research: one-page summary

Five studies on Polymarket and Kalshi public data, September 2026. Four decide with a rule
written before the data that decides it; the fifth is a cross-venue measurement desk. Full
report: [REPORT.md](REPORT.md).

- **Settlement.** Polymarket's 15-minute crypto markets settle on a 60-second Chainlink
  average: it agrees with {ud_agree_twap60} of {ud_windows} outcomes, against {ud_agree_binance}
  for Binance. A spot-priced fair value prices the wrong contract.
- **Taking.** A TWAP-aware fair value beats the market mid late in the window but loses in all
  {ud_taker_cells} cells of a taker grid (t from {ud_taker_t_lo} to {ud_taker_t_hi}) once
  spread, fees and latency apply.
- **Resolved markets.** On {bt_markets} markets, favorites are overpriced rather than cheap
  (favorite carry loses {fc_loss} per trade out of sample, t = {fc_t}); the only in-sample
  winner (t = {bh_is_t}) reverses out of sample (t = {bh_oos_t}).
- **Market making.** On {ps_prints} prints, resting liquidity earns about the maker rebate in
  one price bucket; fills that reach the back of the queue lose {pq_back_loss_x} and
  {pq_back_loss_c} cents per share before it.
- **Cross-venue arbitrage.** Exact Kalshi and Polymarket pairs show {xa_exact_edge_mean} of
  edge that vanishes within a poll; pairs settling on different sources show more edge
  ({xa_basis_edge}) and a negative result ({xa_basis_pnl} per contract).
- **Kalshi maker premium.** {km_verdict}

Tools: Python, DuckDB, Docker on a self-hosted server, public REST and websocket APIs,
cluster-robust inference, reproducible reports generated from raw outputs.
