# pm-edge-report

A synthesis of five studies on Polymarket and Kalshi public data: where a small, slow
participant finds an edge, and where it does not.

- [REPORT.md](REPORT.md): the full report.
- [SUMMARY.md](SUMMARY.md): one page.

Both are generated. `src/pmedge/facts.py` reads every figure from the source outputs in
`sources/` and checks each statement the text makes about a sign or a significance;
`templates/` holds the prose, which contains no measured figure (a test enforces it).

```
pip install -e ".[dev]"
python -m pmedge.build      # regenerate REPORT.md, SUMMARY.md, facts.json
pytest -q                   # fails if they are out of date or a claim no longer holds
```

`facts.json` lists each printed figure with its raw value and the file it came from.
`sources/server-*/MANIFEST.sha256` holds the checksums of the outputs copied from the
server the studies run on.
