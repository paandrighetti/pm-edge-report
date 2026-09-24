Three studies of Kalshi trades find that takers overpay for YES and for longshots (Becker
2026; Burgi, Deng and Whelan 2025; Bartlett and O'Hara 2026), and the two built on tens of
millions of trades find that makers earn a positive return at settlement on average. An average
over all makers is not a strategy. This study asks what is left, after Kalshi's maker fees and
on non-sports markets and trades none of those studies used, for a small maker in two
positions: one who improves the best price by one tick (PENNY, decided by statistic B) and one
whose order waits at the back of the queue (JOIN, decided by statistic C, which uses only the
price levels that a taker order emptied). The backtest has no latency; the slow reaction of a
real small maker is part of the forward test only.

The pre-registration fixed the sample, the statistics, the cells and the rule before any trade
was downloaded, and the decision was taken under the same file (SHA-256 beginning
`{km_prereg_sha}`). A pair (variant, category, side, YES price bucket) qualifies if its mean
profit per contract, after maker fees, is positive with t ≥ 2 in each of two sets of markets
separately, with floors on clusters, events, contracts and losing clusters (at least
{km_floor_losing} losing clusters). The two sets are split by each market's latest expiration
time, assumed fixed at listing; they overlap in trading time. A cluster is a category and a
settlement date. The sample is one UTC hour in twelve from December 2025 to September 2026:
{km_trades} trades, of which {km_trades_ok} remain after the pre-registered exclusions (among
them {km_trades_mve} trades in multivariate markets and {km_trades_late} in markets expiring
after the cutoff), over {km_events} events. Every data-validity check passed.

**Decision** (written {km_gate_time}): {km_qualifying} of {km_pairs_tested} pairs qualify. If no
pair had an edge and each t were standard normal and independent across the two sets of
markets, about {km_expected_false} would qualify by chance; shared settlement dates and heavy
tails make that figure a rough guide. The same trades appear under both variants, so the
{km_qualifying} results cover {km_cells} distinct cells.

{km_qual_table}

Cents per contract of one dollar, after maker fees; t is cluster-robust. Column A is every maker
at the price actually traded, in the same cell. The last column is for the statistic that
decides the pair; the thinnest margin is {km_losing_min} losing clusters against the floor of
{km_floor_losing}.

What the result says:

- **Every qualifying pair has the maker selling YES.** Takers buy YES more often than they sell
  in most non-sports categories, including some with no qualifying pair, so the side of the
  flow alone does not explain where the premium is (share of contracts where the taker bought
  YES, categories with enough events in both sets of markets):

{km_taker_yes_table}

- **It does not rest on the fill assumption alone.** Statistic A, every maker at the price
  actually traded, is positive with t ≥ 2 in both sets of markets in {km_a_sig} of the
  {km_cells} cells.
- **In {km_join_only} the premium goes to resting orders, not to a maker who improves the
  price.** A maker
  who improves the price by one tick earns {km_join_only_b_x} and {km_join_only_b_c} cents per
  contract in the two sets, nothing distinguishable from zero, while statistic C earns
  {km_join_only_c_x} and {km_join_only_c_c}.
- **The average premium is not the finding.** Pooled over all non-sports categories,
  statistic A is {km_rep_x} cents per contract in the exploration markets and {km_rep_c} in
  the confirmation markets; its largest t by side, in absolute value, is {km_rep_tmax}. The
  pooled figure weights contracts, and crypto markets hold {km_crypto_x} of the exploration
  contracts and {km_crypto_c} of the confirmation contracts. The premium lives in a few cells,
  not in the volume.
- **Its size varies between the two sets.** {km_decay_n} of the {km_qualifying} pairs earn
  less in the confirmation markets and {km_rise_n} earn more; one change is significant on its
  own, {km_sig_change}, from {km_sig_change_x} to {km_sig_change_c} cents (t of the difference
  {km_sig_change_t}, treating the two sets as independent, which shared settlement dates make
  approximate). The pooled figure also fell, while crypto's share of the contracts rose.
- **Time to settlement** (exploratory, after the decision; it cannot change the gate). A query
  that reproduces statistic A of the qualifying cells exactly, split by the time from each
  trade to settlement, finds the pooled premium at every horizon from one hour up:
  {km_h1_mean} cents (t = {km_h1_t}) between one and six hours, {km_h6_mean} ({km_h6_t}) up to
  a day, {km_h24_mean} ({km_h24_t}) up to a week and {km_h168_mean} ({km_h168_t}) beyond.
  Trades less than a week before settlement carry {km_short_share} of the pooled contracts, but
  only {km_short_min} in {km_short_min_cell}, and not every cell earns at every horizon. This
  is statistic A on realized time to settlement, which depends on the outcome when a market
  resolves early; the forward universe selects on the scheduled close. It suggests, without
  showing, that the forward test trades where most of the premium was earned.
- **Moved expiration times** (exploratory, after the decision). The pre-registration assumed
  that a market's latest expiration time is not moved after listing; the downloaded data only
  serve the last value and cannot show a move. What they can show is late settlement: the
  backtest counts {km_flagged_all} eligible markets that settled more than a day after their
  latest expiration time, and a query over the markets traded in the qualifying categories
  finds {km_late_markets} of {km_late_universe}; since that universe is at most slightly wider
  than the eligible markets, at least {km_late_lo} ({km_late_lo_share}) of the flagged markets
  are in the qualifying categories, which hold {km_elig_q_share} of the eligible markets. Late
  settlement is concentrated there. These markets carry at most {km_late_max} of the traded
  contracts of any qualifying cell (all trades of the cell, before the PENNY and JOIN
  selections). The pre-registered test of the assumption is the forward test, which logs any
  change of the field.

What the backtest cannot say. PENNY assumes the improved quote stood alone at its price and
would have been filled by the same order; statistic C counts every emptied level, including
levels deeper than the best price. Neither sees competing makers or the size a slow maker would
actually get, and cells chosen as the best of {km_pairs_tested} overstate their own magnitude.
The holdout draws other trades from another twelfth of the hours on the same markets, so it
tests the sampling of trades, not new outcomes; it had downloaded {km_holdout_done} of
{km_holdout_total} hours at {km_holdout_time}; it can remove the part of the selection bias
that comes from sampling trades, not the part that comes from outcomes. The forward paper test
is the only test on new outcomes. It started when the decision was written and quotes only the
qualifying pairs, on up to the {km_fwd_n} most active markets closing within {km_fwd_window}
days (PENNY joins the best price when the spread is one tick). By {km_paper_time} its first
{km_paper_cycles} cycles had produced {km_paper_fills} fills, {km_paper_top_n} of them in
{km_paper_top}, and its cycle log recorded no error. Its success criterion pools the qualifying
pairs, so it will test the pool more than each pair. It succeeds if its profit per contract is positive with t ≥ 2 once
{km_fwd_events} events have settled with at least {km_fwd_neg} losing clusters, and a variant
whose mean is negative after {km_fwd_days} days is abandoned.
