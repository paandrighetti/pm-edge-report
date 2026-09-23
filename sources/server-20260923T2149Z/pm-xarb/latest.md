# pm-xarb daily report, 2026-09-22 (UTC)

Paper desk. Two-venue quotes are quasi-synchronous (one poll apart at most); fills are simulated one poll after detection against the next observed books; settlement values come from each venue's own API.

## Universe

Pairs whitelisted: **69** (generated 2026-09-23T05:01:04.037800+00:00)

| family | kalshi_legs | polymarket_legs | exact | basis | kalshi_unmatched |
|---|---|---|---|---|---|
| crypto | 348 | 99 |  | 15 | 333 |
| macro | 152 | 10 | 5 |  | 142 |
| sports | 114 | 70 | 49 |  | 65 |

## Data quality

| polls | mean_skew_s | max_skew_s | mean_poll_s | kalshi_coverage | poly_coverage |
|---|---|---|---|---|---|
| 28769 | 0.1120 | 0.6260 | 0.2700 | 1.0000 | 0.9030 |

## Detections (net of fees, depth-limited)

| family | klass | combo | n | mean_edge | max_edge | mean_qty | sum_edge_usd | mean_days_locked |
|---|---|---|---|---|---|---|---|---|
| crypto | basis | kalshi:no+polymarket:yes | 5575 | 0.0197 | 0.1059 | 237.20 | 24,432.89 | 0.4000 |
| crypto | basis | kalshi:yes+polymarket:no | 21205 | 0.0302 | 0.3821 | 385.60 | 366,649.07 | 0.5000 |
| sports | exact | kalshi:no+polymarket:yes | 32 | 0.0039 | 0.0115 | 469.10 | 58.23 | 0.3000 |
| sports | exact | kalshi:yes+polymarket:no | 59 | 0.0069 | 0.0115 | 445.80 | 186.55 | 0.4000 |

### Episodes (contiguous polls with the same opportunity)

| family | klass | episodes | median_life_s | p90_life_s | max_life_s | mean_peak_edge | sum_peak_edge_usd |
|---|---|---|---|---|---|---|---|
| crypto | basis | 276 | 12.00 | 327.40 | 20,617.40 | 0.0113 | 1,214.41 |
| sports | exact | 19 | 0.0000 | 60.10 | 72.10 | 0.0053 | 33.73 |

### Largest episodes

| pair_id | klass | combo | peak_edge | max_qty | peak_usd | life_s | kalshi | polymarket |
|---|---|---|---|---|---|---|---|---|
| crypto-4f9cf0571c | basis | kalshi:yes+polymarket:no | 0.3821 | 809 | 309.14 | 4,715.00 |  |  |
| crypto-6b1873d551 | basis | kalshi:no+polymarket:yes | 0.0832 | 545 | 45.34 | 744.80 |  |  |
| crypto-4f9cf0571c | basis | kalshi:yes+polymarket:no | 0.0699 | 537 | 37.53 | 393.40 |  |  |
| crypto-6b1873d551 | basis | kalshi:no+polymarket:yes | 0.1059 | 537 | 37.04 | 2,336.50 |  |  |
| crypto-4f9cf0571c | basis | kalshi:no+polymarket:yes | 0.0665 | 536 | 36.05 | 228.30 |  |  |
| crypto-3d1a985663 | basis | kalshi:yes+polymarket:no | 0.0604 | 533 | 33.04 | 14,430.60 |  |  |
| crypto-4f9cf0571c | basis | kalshi:yes+polymarket:no | 0.0503 | 530 | 30.81 | 231.20 |  |  |
| crypto-3d1a985663 | basis | kalshi:yes+polymarket:no | 0.0487 | 525 | 25.55 | 3,360.60 |  |  |
| crypto-3d1a985663 | basis | kalshi:yes+polymarket:no | 0.0371 | 519 | 19.23 | 20,617.40 |  |  |
| crypto-4f9cf0571c | basis | kalshi:yes+polymarket:no | 0.0293 | 518 | 18.50 | 264.30 |  |  |

## Paper execution

### Intent outcomes

| model | status | n | hedged_contracts | notional | fees | mean_edge_seen | mean_hedge_cost |
|---|---|---|---|---|---|---|---|
| joint | filled | 4 | 1506 | 1,475.94 | 21.93 | 0.0056 | 0.9944 |
| joint | missed | 7 | 0 |  |  | 0.0059 |  |

### Leg failures (second leg gone once the first is on; the cost sits in the unwinds)

| klass | family | intents | filled | leg_failures | missed | leg_failure_rate | hedged | fill_ratio |
|---|---|---|---|---|---|---|---|---|
| exact | sports | 11 | 4 | 0 | 7 | 0.0000 | 1506 | 0.5310 |

### Unwinds of naked legs

| unwinds | pnl | mean_polls |
|---|---|---|
| 0 |  |  |

### Resolutions today (one_sided: pairs where only one venue has reported so far)

| family | klass | resolved_pairs | divergent | one_sided | naked_pairs | pnl_naked | pnl_hedged | pnl |
|---|---|---|---|---|---|---|---|---|
| sports | exact | 2 | 0 | 0 | 0 |  | 2.3700 | 2.3700 |

### Resolutions since inception

| family | klass | resolved_pairs | divergent | one_sided | naked_pairs | pnl_naked | pnl_hedged | pnl |
|---|---|---|---|---|---|---|---|---|
| crypto | basis | 8 | 0 | 6 | 0 |  | -301.70 | -301.70 |
| sports | exact | 46 | 0 | 14 | 7 | -58.07 | -35.02 | -93.09 |

### Return on locked capital (resolved legs, since inception)

| pnl | dollar_days | annualized_return_on_locked |
|---|---|---|
| -394.79 | 3,534.40 | -40.77 |

### Latest mark-to-market

| at | open_positions | locked | unrealized | realized | cash |
|---|---|---|---|---|---|
| 2026-09-23 06:00 | 10 | 549.00 | -0.5400 | -616.21 | {'kalshi': 9299.23, 'polymarket': 9535.57} |

## Classes not traded: counterfactual

| klass | pairs | divergent | divergence_rate | mean_edge_at_entry | mean_pnl_per_contract | worst_pair_per_contract |
|---|---|---|---|---|---|---|
| exact | 17 | 0 | 0.0000 | 0.0064 | 0.0064 | 0.0000 |
| basis | 22 | 2 | 0.0910 | 0.0194 | -0.0716 | -0.9971 |

Priced at the first opportunity seen on each pair. `mean_pnl_per_contract` is what a hedge held to settlement would have returned per contract, each leg paid by its own venue; a divergent pair pays 0 or 2, which is the tail the entry edge is being paid for.

## Reading guide

* `exact` pairs share resolution source and instant; a hedged pair pays 1 per contract. `basis` pairs do not, and `divergent` counts resolutions where the two venues disagreed.

* Edges are net of taker fees on both legs at the walked prices. They are not net of the capital cost of waiting.

* Realized PnL books each leg at its own venue's settlement. A pair whose `one_sided` flag is set has had only its losing or winning leg booked; the total is meaningful once `one_sided` returns to zero.

* Latency is one poll interval by construction; a real taker would be faster, but would also face size that vanished between quote and order, which is what the `missed` and `partial` rows measure.
