# wc2026-viz-tournament-flow

A small gallery of beautiful, honest visualizations of the FIFA World Cup 2026
tournament — focused on **tournament shape**: group standings, group→knockout
flow, results matrices, goal stories, upsets.

Each `plots/*.py` module renders one viz to `artifacts/` as both PNG@200dpi and
SVG. Run any module standalone with `python plots/<name>.py`.

## Reproduce

```bash
pip install --break-system-packages matplotlib seaborn mplsoccer plotnine \
    highlight-text squarify pandas pyarrow numpy
python plots/<name>.py
```

Dataset: Kaggle `mominullptr/fifa-world-cup-2026-dataset` (CSVs vendored in
`data/`). Tournament was at the end of group stage (72/72 group matches
completed, 1 R32 match played) as of 2026-06-29.
