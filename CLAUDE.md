# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Personal data analysis project for visualizing Spotify Extended Streaming History. Input is the JSON data exported from Spotify's "Download your data" feature (extended streaming history option).

## Running the Project

```bash
python main.py
```

**Before running**, set the paths at the top of `main.py`:
- `STREAMING_HISTORY_DIR` — directory containing `endsong_*.json` from the extended streaming history export
- `PLAYLIST_FILE` — path to `Playlist1.json` from the account data export (leave empty to skip)
- `LIBRARY_FILE` — path to `YourLibrary.json` from the account data export (leave empty to skip)

The program loads data on startup, then presents an interactive numbered menu. No commenting/uncommenting required.

## Dependencies

No `requirements.txt` exists. Install manually:

```bash
pip install pandas matplotlib numpy seaborn
```

## Architecture

Three-module pipeline:

1. **`spotify_scraper.py`** — Data extraction and cleaning
   - `extract_data(file_dir)`: Reads all `.json` files from a directory, concatenates into a single DataFrame
   - `clean_data(sp_data)`: Adds `Count` (always 1, for aggregation) and `datetime` (parsed from `ts`) columns

2. **`spotify_analysis.py`** — Visualization functions, all accept the cleaned DataFrame

   | Function | Description |
   |---|---|
   | `top_songs(sp_df, num, type)` | Bar chart of top songs by `"Count"` or `"ms_played"` |
   | `top_artists(sp_df, num, type)` | Bar chart of top artists |
   | `uniq_artist(sp_df)` | Pie: unique vs. repeated artist plays |
   | `uniq_song_from_artist(sp_df, num, type)` | Unique track count per top-N artists |
   | `daytime_usage(sp_df)` | Histogram by hour of day (0–23) |
   | `listening_heatmap(sp_df)` | Seaborn heatmap: day-of-week × hour |
   | `year_usage(sp_df)` | Songs played per calendar month (1–12) |
   | `yearly_comparison(sp_df)` | Side-by-side: play count and hours per year |
   | `max_song_day(sp_df)` | Scatter: songs played per day over time |
   | `cumulative_listening(sp_df)` | Line chart of total hours accumulated over time |
   | `skip_analysis(sp_df, skip_threshold_ms)` | Skip rate pie + most-skipped songs (default threshold: 30s) |

3. **`spotify_playlists.py`** — Playlist features using `Playlist1.json` from Spotify account data export

   | Function | Description |
   |---|---|
   | `load_playlists(file_path)` | Parse `Playlist1.json`, return list of playlist dicts |
   | `list_playlists(playlists)` | Print numbered table of all playlists |
   | `show_playlist(playlists, identifier)` | Print all tracks; identifier = number or name (partial match supported) |
   | `export_playlist(playlists, identifier, output_path)` | Export playlist tracks to CSV |
   | `playlist_stats(playlists)` | Summary: total playlists, tracks, longest playlists |

4. **`spotify_library.py`** — Liked songs features using `YourLibrary.json` from Spotify account data export

   | Function | Description |
   |---|---|
   | `load_library(file_path)` | Parse `YourLibrary.json`, return DataFrame with `artist/album/track/uri` |
   | `library_stats(library_df)` | Summary stats + bar chart of artists with most liked songs |
   | `browse_library(library_df, artist_filter)` | Print all liked tracks, optionally filtered by artist |
   | `liked_vs_streamed(library_df, streaming_df, num)` | Cross-reference: which liked songs you actually stream most, and which you've never played |

5. **`main.py`** — Interactive CLI menu; loads data once, loops on menu until `q`

## Key Data Columns

The Spotify extended streaming history JSON files provide:

| Column | Description |
|---|---|
| `ts` | ISO timestamp string of stream end |
| `master_metadata_album_artist_name` | Artist name |
| `master_metadata_track_name` | Track name |
| `ms_played` | Milliseconds played |

Added by `clean_data()`: `Count` (int, always 1), `datetime` (pandas datetime).
Additional derived columns (`hour`, `month`, `date`, `year`, etc.) are added temporarily inside individual analysis functions using `.copy()` to avoid mutating the shared DataFrame.

## Notes

- The `type` parameter in analysis functions accepts `"Count"` (play count) or `"ms_played"` (duration). ms is converted to hours with `* 2.77e-7`.
- `spotify_playlists._find_playlist()` accepts a 1-based index, exact name, or partial name match.
- The nested `Spotify-Streaming-history-analysis-main/` directory is a separate reference project with a Jupyter notebook; it is not integrated with the Python scripts.
