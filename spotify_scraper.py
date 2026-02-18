
# spotify_scraper.py
#   Loads Spotify streaming history JSON files and normalizes them into
#   a standard DataFrame used by spotify_analysis.py.
#
#   Supports two export formats automatically:
#     Extended Streaming History  — files named endsong_*.json
#       columns: ts, ms_played, master_metadata_track_name,
#                master_metadata_album_artist_name, ...
#     Basic Account Data history  — files named StreamingHistory*.json
#       columns: endTime, msPlayed, trackName, artistName
#       (these get renamed to the extended format names on load)

import pandas as pd
import os

# Column mapping: basic Account Data export → extended history names
_BASIC_COLUMNS = {
    "endTime":    "ts",
    "artistName": "master_metadata_album_artist_name",
    "trackName":  "master_metadata_track_name",
    "msPlayed":   "ms_played",
}


def extract_data(file_dir):
    file_dir = os.path.expanduser(file_dir)

    all_json = [f for f in os.listdir(file_dir) if f.endswith(".json")]
    print(f"JSON files in directory: {all_json}")

    dfs = []
    for file in all_json:
        try:
            df = pd.read_json(os.path.join(file_dir, file))
            if isinstance(df, pd.DataFrame) and not df.empty:
                dfs.append(df)
                print(f"  Loaded: {file}  ({len(df):,} rows)")
        except (ValueError, Exception) as e:
            print(f"  Skipped: {file}  ({e})")

    spotify_df = pd.concat(dfs, ignore_index=True)

    # Normalize basic-format column names so all analysis functions work
    # regardless of which export type was used.
    if "endTime" in spotify_df.columns:
        print("Detected basic Account Data format — normalizing column names.")
        spotify_df = spotify_df.rename(columns=_BASIC_COLUMNS)

    return spotify_df


def clean_data(sp_data):
    sp_data["Count"] = 1
    sp_data["datetime"] = pd.to_datetime(sp_data["ts"], utc=True)

    print(f"INFO: {sp_data.shape[0]:,} rows, {sp_data.shape[1]} columns")
    print(f"INFO: unique counts:\n{sp_data.nunique()}")

    return sp_data
