# MUL Retrieval Browser

Alpha Strike unit browser that pulls data from [masterunitlist.info](http://masterunitlist.info). Two components: a Jupyter notebook that scrapes and builds the dataset, and a Streamlit app for browsing it.

## Running the app

```
uv run streamlit run app/app.py
```

## Running the data pipeline

Execute the notebook headlessly (2-hour timeout for the slow era scraping cell):

```
uv run jupyter nbconvert --to notebook --execute --ExecutePreprocessor.timeout=7200 --output "Data retrieval from MUL.ipynb" "jupyter/Data retrieval from MUL.ipynb"
```

Output CSV lands in `jupyter/`. Move or copy it to `data/` so the app picks it up.

## Data file convention

The app auto-selects the most recently modified `unit_list*.csv` from `data/`. Drop a new CSV there and restart the app to update the data.

## App module structure

| File | Purpose |
|---|---|
| `app/app.py` | Entry point: page config, session state, tabs |
| `app/mul_service.py` | `load_data()` — finds and parses the CSV |
| `app/constants.py` | `ERA_COLS`, `TYPE_HIERARCHY` |
| `app/filters.py` | Sidebar filter rendering + filter logic |
| `app/browser_view.py` | Browse tab: unit table and detail panel |
| `app/lance_builder_view.py` | Lance Builder tab: tracked unit list |

## MUL API notes

- **JSON API** (`masterunitlist.azurewebsites.net/Unit/QuickList`) — returns unit stats (PV, damage, move, etc.) but has no era/faction availability data
- **Era data** requires scraping individual HTML pages from `masterunitlist.info` — this is slow (~12s per request) and is what makes the notebook take a long time to run
- The notebook uses `ThreadPoolExecutor(max_workers=10)` for the era scraping cell to parallelize requests
- All requests use a `requests.Session` with `Retry(total=3, backoff_factor=1)` for automatic retries on failure
