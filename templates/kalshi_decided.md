Three studies of Kalshi trades find that takers overpay for YES and for longshots (Becker
2026; Burgi, Deng and Whelan 2025; Bartlett and O'Hara 2026), and the two built on tens of
millions of trades find that makers earn a positive return at settlement on average. An average
over all makers is not a strategy. This study asks what is left for a maker who improves the
best price by one tick (PENNY) or joins at the back of the queue (JOIN), reacts in tens of
seconds and pays Kalshi's maker fees, on non-sports markets and on trades none of those studies
used.

The pre-registration fixed the sample, the statistics, the cells and the rule before any trade
was downloaded, and the decision was taken under the same file (SHA-256 beginning
`{km_prereg_sha}`). A pair (variant, category, side, YES price bucket) qualifies if its mean
profit per contract, after maker fees, is positive with t ≥ 2 in each of two periods separately,
with floors on clusters, events, contracts and losing clusters; a cluster is a category and a
settlement date, and the periods are split by each market's latest expiration time, fixed at
listing. The sample is one UTC hour in twelve from December 2025 to September 2026:
{km_trades} trades, {km_trades_ok} of them in eligible markets after excluding
{km_trades_mve} trades in multivariate markets, over {km_events} events. Every data-validity
check passed.

**Decision** (written {km_gate_time}): {km_qualifying} of {km_pairs_tested} pairs qualify. If
the pairs were independent and had no edge, about {km_expected_false} would qualify by chance.
They are not independent (the same trades appear under both variants), so the
{km_qualifying} results cover {km_cells} distinct cells.

{km_qual_table}

Cents per contract of one dollar, after maker fees; t is cluster-robust. PENNY is decided by
statistic B, JOIN by statistic C; column A is every maker at the price actually traded, in the
same cell.

What the result says:

- **Every qualifying pair has the maker selling YES.** In the qualifying categories, takers
  bought YES in {km_yes_lo} to {km_yes_hi} of the contracts (above half in {km_yes_above_half}
  of {km_yes_cases} category-periods), against {km_yes_other_lo} to {km_yes_other_hi} in
  crypto and financials (share of contracts where the taker bought YES):

{km_taker_yes_table}

- **It does not rest on the one-tick assumption alone.** Statistic A, every maker at the price
  actually traded, is positive with t ≥ 2 in both periods in {km_a_sig} of the {km_cells}
  cells.
- **In {km_join_only} the premium goes to orders already resting at the best price.** A maker
  who improves the price by one tick earns {km_join_only_b_x} and {km_join_only_b_c} cents per
  contract in the two periods, nothing distinguishable from zero, while the last order in the
  queue at the best price earns {km_join_only_c_x} and {km_join_only_c_c}.
- **The average premium is not the finding.** Pooled over all non-sports categories,
  statistic A is {km_rep_x} cents per contract in the exploration period and {km_rep_c} in
  the confirmation period, never significant (largest t in absolute value {km_rep_tmax}). The
  pooled figure weights contracts, and crypto markets hold {km_crypto_x} of the exploration
  contracts and {km_crypto_c} of the confirmation contracts. The premium lives in a few
  categories, not in the volume.
- **It is shrinking in most pairs.** {km_decay_n} of the {km_qualifying} pairs earn less in the
  confirmation period than in the exploration period, and so does the pooled figure.
- **A check made after the decision** (exploratory; it cannot change the gate): the
  pre-registration assumed that a market's latest expiration time is not moved after listing.
  In the qualifying categories, {km_late_markets} of {km_late_universe} markets settled
  more than a day after it, and they carry at most {km_late_max} of the traded contracts of any
  qualifying cell (measured on all trades of the cell, before the PENNY and JOIN selections).

What the backtest cannot say. PENNY assumes the improved quote stood alone at its price and
would have been filled by the same order; JOIN only sees the levels that an order emptied, a
lower bound. Neither sees competing makers or the size a slow maker would actually get, and
cells chosen as the best of {km_pairs_tested} overstate their own magnitude. The forward paper
test replaces the fill assumptions with the live order book: it started when the decision was
written, quotes only the qualifying pairs, and succeeds if its profit per contract is positive
with t ≥ 2 once {km_fwd_events} events have settled with at least {km_fwd_neg} losing
clusters; a variant whose mean is negative after {km_fwd_days} days is abandoned. The
holdout, trades from another twelfth of the hours, is downloading; a qualifying pair whose
holdout mean is negative will be reported as contradicted.
