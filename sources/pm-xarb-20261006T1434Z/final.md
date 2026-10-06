# pm-xarb, exact class

9 archived sports pairs joined two different games:
- sports-23fc8b34c4 sports|MLB|2026-09-26|WSH: kalshi KXMLBGAME-26SEP261605NYMWSH-WSH, polymarket start 2026-09-26T16:35:00+00:00
- sports-3e8d969198 sports|MLB|2026-09-22|TOR: kalshi KXMLBGAME-26SEP221835TORBAL-TOR, polymarket start 2026-09-23T22:35:00+00:00
- sports-5847ec3e8e sports|MLB|2026-09-23|HOU: kalshi KXMLBGAME-26SEP232210HOUSEA-HOU, polymarket start 2026-09-23T01:40:00+00:00
- sports-6299bded05 sports|MLB|2026-09-26|BAL: kalshi KXMLBGAME-26SEP261915BALNYY-BAL, polymarket start 2026-09-25T23:05:00+00:00
- sports-92c069c3e2 sports|MLB|2026-09-23|TOR: kalshi KXMLBGAME-26SEP231835TORBAL-TOR, polymarket start 2026-09-23T17:35:00+00:00
- sports-f280179b3d sports|MLB|2026-09-25|BAL: kalshi KXMLBGAME-26SEP251905BALNYY-BAL, polymarket start 2026-09-25T20:05:00+00:00
- sports-fd549fa410 sports|MLB|2026-09-22|BAL: kalshi KXMLBGAME-26SEP221835TORBAL-BAL, polymarket start 2026-09-23T22:35:00+00:00
- sports-fdf9838df4 sports|MLB|2026-09-23|SEA: kalshi KXMLBGAME-26SEP232210HOUSEA-SEA, polymarket start 2026-09-23T01:40:00+00:00
- sports-fe783d494b sports|MLB|2026-09-23|BAL: kalshi KXMLBGAME-26SEP231835TORBAL-BAL, polymarket start 2026-09-23T17:35:00+00:00

### Resolutions

| other_game | pairs | divergent | pnl_usd |
|---|---|---|---|
| False | 76 | 0 | -60.01 |
| True | 5 | 0 | 24.92 |

### Filled intents

| other_game | filled | contracts | missed |
|---|---|---|---|
| False | 65 | 15058 | 83 |
| True | 5 | 1790 | 3 |

### Detections

| other_game | n | mean_edge_cents |
|---|---|---|
| False | 1568 | 0.591 |
| True | 12051 | 26.953 |

### Episodes

| other_game | episodes | median_life_s | p90_life_s | single_poll_pct |
|---|---|---|---|---|
| False | 530 | 0.0 | 9.0 | 75.1 |
| True | 96 | 9.0 | 147.2 | 22.9 |

### Pairs observed to settlement

| other_game | pairs | divergent |
|---|---|---|
| False | 104 | 0 |
| True | 4 | 2 |

### Counterfactual since inception, pairs that joined two games left out

| klass | pairs | divergent | divergence_rate | mean_edge_at_entry | mean_pnl_per_contract | worst_pair_per_contract |
|---|---|---|---|---|---|---|
| exact | 104 | 0 | 0.0000 | 0.0098 | 0.0098 | 0.0000 |
| basis | 88 | 3 | 0.0340 | 0.0102 | -0.0012 | -0.9971 |

Priced at the first opportunity seen on each pair. `mean_pnl_per_contract` is what a hedge held to settlement would have returned per contract, each leg paid by its own venue; a divergent pair pays 0 or 2, which is the tail the entry edge is being paid for.

