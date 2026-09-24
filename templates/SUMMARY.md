# Prediction-market research: one-page summary

Five studies on Polymarket and Kalshi public data, September 2026. Three decide with a rule
stated before the statistic it governs; the other two are measurements. Full report:
[REPORT.md](REPORT.md).

- **Settlement.** Polymarket's 15-minute crypto markets settle on a 60-second Chainlink
  average: it agrees with {ud_agree_twap60} of {ud_windows} outcomes in the latest week
  ({ud0_agree_twap60} over the first six days), against {ud_agree_binance} for Binance. A spot-priced fair value prices the wrong contract.
- **Taking.** A TWAP-aware fair value roughly matches the market mid in accuracy and loses in
  all {ud_taker_cells} cells of a taker grid (t from {ud_taker_t_lo} to {ud_taker_t_hi}) once
  spread, fees and latency apply.
- **Resolved markets.** On {bt_markets} markets, favorites are overpriced rather than cheap
  at the last hourly print (favorite carry loses {fc_loss} per trade out of sample,
  t = {fc_t}); the best hedge cell (t = {bh_is_t}) reverses (t = {bh_oos_t}); a Dutch-book
  residual survives only in a few cheap books, unsized.
- **Market making.** On {ps_prints} prints, resting liquidity earns about the maker rebate in
  one price bucket; fills that reach the back of the queue lose {pq_back_loss_x} and
  {pq_back_loss_c} cents per share before it.
- **Cross-venue arbitrage.** Exact Kalshi and Polymarket pairs show {xa_exact_cf_edge} of
  entry edge, sound at settlement but hard to fill (median episode a single poll); pairs
  settling on different sources or at different instants show more edge ({xa_basis_edge}) and a negative result
  ({xa_basis_pnl} per contract, {xa_basis_div} divergent settlements).
- **Kalshi maker premium.** On {km_trades_ok} eligible trades, {km_qualifying} of
  {km_pairs_tested} pre-registered pairs pass in both sets of markets, all with the maker selling YES,
  in {km_qual_cats}. The pooled
  premium over all non-sports markets is not significant. A forward paper test is running.

Tools: Python, DuckDB, Docker on a self-hosted server, public REST and websocket APIs,
cluster-robust inference, reproducible reports generated from raw outputs.
