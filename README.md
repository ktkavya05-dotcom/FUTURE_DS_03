# Flowline — Funnel Intelligence

A Streamlit analytics dashboard for e-commerce event funnel performance.

## Overview

This project visualizes funnel conversion against user event data from `2019-Nov.csv`.
It calculates unique users by event stage, models channel attribution for illustrative analysis, and highlights key conversion and drop-off insights.

## Included files

- `app.py` — Streamlit dashboard application
- `requirements.txt` — Python dependencies
- `2019-Nov.csv` — event-level source data (required for the app)
- `index.html` — static dashboard preview / design reference

## Requirements

- Python 3.10+ recommended
- `streamlit`
- `pandas`
- `plotly`

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Run the app

From the project root:

```bash
streamlit run app.py
```

Then open the local URL shown by Streamlit in your browser.

## What it does

- Reads a sample set of event rows from `2019-Nov.csv`
- Filters to e-commerce event types: `view`, `cart`, and `purchase`
- Builds a funnel view of product viewers, cart additions, and customers
- Computes conversion rates and revenue from purchase events
- Displays a time-series conversion trend and funnel drop-off chart
- Shows illustrative channel quality and recommended next actions

## Notes

- The app only reads a sample of the source file by default to remain responsive.
- Channel attribution in the dashboard is modeled from `user_id` values because the raw CSV has no source/channel column.
- Ensure `2019-Nov.csv` is present next to `app.py` before launching the app.
