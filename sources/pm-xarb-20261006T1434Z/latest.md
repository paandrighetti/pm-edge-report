# pm-xarb daily report, 2026-10-05 (UTC)

Paper desk. Two-venue quotes are quasi-synchronous (one poll apart at most); fills are simulated one poll after detection against the next observed books; settlement values come from each venue's own API.

## Universe

Pairs whitelisted: **51** (generated 2026-10-06T05:01:43.412527+00:00)

| family | kalshi_legs | polymarket_legs | exact | basis | kalshi_unmatched |
|---|---|---|---|---|---|
| crypto | 218 | 85 |  | 12 | 206 |
| macro | 162 | 15 | 5 |  | 147 |
| sports | 111 | 46 | 34 |  | 77 |

## Data quality

| polls | mean_skew_s | max_skew_s | mean_poll_s | kalshi_coverage | poly_coverage |
|---|---|---|---|---|---|
| 28766 | 0.0940 | 5.0610 | 0.2350 | 1.0000 | 0.7930 |

## Detections (net of fees, depth-limited)

| family | klass | combo | n | mean_edge | max_edge | mean_qty | sum_edge_usd | mean_days_locked |
|---|---|---|---|---|---|---|---|---|
| crypto | basis | kalshi:no+polymarket:yes | 15538 | 0.0211 | 0.1923 | 281.50 | 155,093.10 | 1.9000 |
| crypto | basis | kalshi:yes+polymarket:no | 7499 | 0.0109 | 0.1008 | 331.60 | 37,934.78 | 0.4000 |
| sports | exact | kalshi:no+polymarket:yes | 3 | 0.0085 | 0.0121 | 275.70 | 8.5700 | 0.3000 |
| sports | exact | kalshi:yes+polymarket:no | 4 | 0.0082 | 0.0121 | 336.80 | 14.72 | 0.3000 |

### Episodes (contiguous polls with the same opportunity)

| family | klass | episodes | median_life_s | p90_life_s | max_life_s | mean_peak_edge | sum_peak_edge_usd |
|---|---|---|---|---|---|---|---|
| crypto | basis | 314 | 18.00 | 292.50 | 9,634.40 | 0.0082 | 898.49 |
| sports | exact | 7 | 0.0000 | 0.0000 | 0.0000 | 0.0084 | 23.29 |

### Largest episodes

| pair_id | klass | combo | peak_edge | max_qty | peak_usd | life_s | kalshi | polymarket |
|---|---|---|---|---|---|---|---|---|
| crypto-3907332097 | basis | kalshi:no+polymarket:yes | 0.1923 | 624 | 124.79 | 5,363.80 |  |  |
| crypto-3907332097 | basis | kalshi:yes+polymarket:no | 0.1008 | 556 | 56.02 | 1,808.00 |  |  |
| crypto-3907332097 | basis | kalshi:no+polymarket:yes | 0.0450 | 533 | 33.69 | 192.20 |  |  |
| crypto-3907332097 | basis | kalshi:yes+polymarket:no | 0.0540 | 532 | 32.02 | 573.60 |  |  |
| crypto-3907332097 | basis | kalshi:no+polymarket:yes | 0.0400 | 520 | 20.83 | 189.20 |  |  |
| crypto-3907332097 | basis | kalshi:yes+polymarket:no | 0.0395 | 520 | 20.52 | 531.60 |  |  |
| crypto-84d5201ed8 | basis | kalshi:no+polymarket:yes | 0.0238 | 517 | 17.70 | 8,424.10 |  |  |
| crypto-3907332097 | basis | kalshi:yes+polymarket:no | 0.0271 | 516 | 16.03 | 210.20 |  |  |
| crypto-3907332097 | basis | kalshi:no+polymarket:yes | 0.0283 | 514 | 14.53 | 204.20 |  |  |
| crypto-f623145a35 | basis | kalshi:yes+polymarket:no | 0.0269 | 513 | 13.80 | 3,255.50 |  |  |

## Paper execution

### Intent outcomes

| model | status | n | hedged_contracts | notional | fees | mean_edge_seen | mean_hedge_cost |
|---|---|---|---|---|---|---|---|
| joint | missed | 1 | 0 |  |  | 0.0113 |  |

### Leg failures (second leg gone once the first is on; the cost sits in the unwinds)

| klass | family | intents | filled | leg_failures | missed | leg_failure_rate | hedged | fill_ratio |
|---|---|---|---|---|---|---|---|---|
| exact | sports | 1 | 0 | 0 | 1 | 0.0000 | 0 | 0.0000 |

### Unwinds of naked legs

| unwinds | pnl | mean_polls |
|---|---|---|
| 0 |  |  |

### Resolutions today (one_sided: pairs where only one venue has reported so far)

| family | klass | resolved_pairs | divergent | one_sided | naked_pairs | pnl_naked | pnl_hedged | pnl |
|---|---|---|---|---|---|---|---|---|
| sports | exact | 1 | 0 | 0 | 0 |  | 0.1700 | 0.1700 |

### Resolutions since inception

| family | klass | resolved_pairs | divergent | one_sided | naked_pairs | pnl_naked | pnl_hedged | pnl |
|---|---|---|---|---|---|---|---|---|
| crypto | basis | 8 | 0 | 6 | 0 |  | -301.70 | -301.70 |
| sports | exact | 80 | 0 | 18 | 7 | -58.07 | 22.96 | -35.11 |

### Return on locked capital (resolved legs, since inception)

| pnl | dollar_days | annualized_return_on_locked |
|---|---|---|
| -336.81 | 7,442.27 | -16.52 |

### Latest mark-to-market

| at | open_positions | locked | unrealized | realized | cash |
|---|---|---|---|---|---|
| 2026-10-06 06:00 | 6 | 224.23 | -0.4400 | -558.23 | {'kalshi': 9194.11, 'polymarket': 10023.43} |

## Classes not traded: counterfactual

| klass | pairs | divergent | divergence_rate | mean_edge_at_entry | mean_pnl_per_contract | worst_pair_per_contract |
|---|---|---|---|---|---|---|
| exact | 108 | 2 | 0.0190 | 0.0193 | 0.0008 | -0.4798 |
| basis | 88 | 3 | 0.0340 | 0.0102 | -0.0012 | -0.9971 |

Priced at the first opportunity seen on each pair. `mean_pnl_per_contract` is what a hedge held to settlement would have returned per contract, each leg paid by its own venue; a divergent pair pays 0 or 2, which is the tail the entry edge is being paid for.

## Reading guide

* `exact` pairs share resolution source and instant; a hedged pair pays 1 per contract. `basis` pairs do not, and `divergent` counts resolutions where the two venues disagreed.

* Edges are net of taker fees on both legs at the walked prices. They are not net of the capital cost of waiting.

* Realized PnL books each leg at its own venue's settlement. A pair whose `one_sided` flag is set has had only its losing or winning leg booked; the total is meaningful once `one_sided` returns to zero.

* Latency is one poll interval by construction; a real taker would be faster, but would also face size that vanished between quote and order, which is what the `missed` and `partial` rows measure.
