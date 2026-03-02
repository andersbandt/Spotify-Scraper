# Spotify-Scraper

Python tool for analyzing your Spotify Extended Streaming History with an interactive terminal menu.

## Setup

1. Request your data from Spotify: **Account → Privacy & Security → Download your data**
   - Check **Extended streaming history** for the richest data (takes ~30 days)
   - The basic **Account data** export also works (StreamingHistory\*.json format)
2. Install dependencies: `pip install pandas matplotlib numpy seaborn`
3. Set your data paths at the top of `main.py`
4. Run: `python main.py`

## References

- [spotify-wrapped-eda](https://github.com/carlynbandt/Spotify-Streaming-history-analysis) — Jupyter notebook EDA project that informed several analyses in this repo (day-of-week breakdown, weekday vs. weekend split, listening summary stats, unique song ratio)
