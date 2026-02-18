
# spotify_library.py
#   Functions for loading and analyzing Spotify "Your Library" data
#   from the "Account Data" export (YourLibrary.json).
#
#   YourLibrary.json structure:
#   {
#     "tracks": [
#       { "artist": "...", "album": "...", "track": "...", "uri": "..." }
#     ]
#   }

import json
import os
import pandas as pd
import matplotlib.pyplot as plt


def load_library(file_path):
    """
    Load YourLibrary.json from a Spotify account data export.
    Returns a DataFrame of liked tracks.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Library file not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    tracks = data.get("tracks", [])
    df = pd.DataFrame(tracks, columns=["artist", "album", "track", "uri"])
    print(f"Loaded {len(df):,} liked tracks.")
    return df


def library_stats(library_df):
    """Print summary stats for the liked songs library."""
    total    = len(library_df)
    artists  = library_df["artist"].nunique()
    albums   = library_df["album"].nunique()

    print(f"\n  ── Your Library Stats ──────────────────────────")
    print(f"  Total liked songs  : {total:,}")
    print(f"  Unique artists     : {artists:,}")
    print(f"  Unique albums      : {albums:,}")

    top_artists = (library_df.groupby("artist")["track"]
                              .count()
                              .sort_values(ascending=False)
                              .head(10))
    print(f"\n  Top 10 artists by liked song count:")
    for artist, count in top_artists.items():
        bar = "█" * count
        print(f"    {artist:<35} {count:>3}  {bar}")

    # Quick bar chart
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.barh(top_artists.index[::-1], top_artists.values[::-1],
            color="mediumseagreen")
    ax.set(title="Artists with Most Liked Songs",
           xlabel="Liked Song Count", ylabel="")
    plt.tight_layout()
    plt.show()


def browse_library(library_df, artist_filter=None):
    """
    Print liked tracks in a table.
    If `artist_filter` is provided, show only tracks by that artist
    (case-insensitive, partial match).
    """
    df = library_df.copy()

    if artist_filter:
        df = df[df["artist"].str.contains(artist_filter, case=False, na=False)]
        if df.empty:
            print(f"\n  No liked songs found matching artist '{artist_filter}'.")
            return
        print(f"\n  Liked songs matching '{artist_filter}'  ({len(df)} tracks)")
    else:
        print(f"\n  All liked songs  ({len(df):,} tracks)")

    print(f"\n  {'#':<5} {'Track':<45} {'Artist':<30} Album")
    print("  " + "─" * 95)

    for i, (_, row) in enumerate(df.iterrows(), 1):
        t_name = str(row["track"])[:43]
        artist = str(row["artist"])[:28]
        album  = str(row["album"])[:25]
        print(f"  {i:<5} {t_name:<45} {artist:<30} {album}")

    print()


def liked_vs_streamed(library_df, streaming_df, num=20):
    """
    Cross-reference liked songs against streaming history.
    Shows which of your liked songs you actually stream the most,
    and highlights liked songs you've never streamed.

    Matching is done on track name (case-insensitive) since URIs differ
    between the two export types.
    """
    TRACK_COL  = "master_metadata_track_name"
    ARTIST_COL = "master_metadata_album_artist_name"

    # Build a play-count lookup from streaming history
    play_counts = (streaming_df.groupby(TRACK_COL)["Count"]
                               .sum()
                               .reset_index()
                               .rename(columns={TRACK_COL: "track_lower",
                                                "Count": "play_count"}))
    play_counts["track_lower"] = play_counts["track_lower"].str.lower()

    liked = library_df.copy()
    liked["track_lower"] = liked["track"].str.lower()

    merged = liked.merge(play_counts, on="track_lower", how="left")
    merged["play_count"] = merged["play_count"].fillna(0).astype(int)

    # Stats
    streamed     = (merged["play_count"] > 0).sum()
    never_played = (merged["play_count"] == 0).sum()
    total        = len(merged)

    print(f"\n  ── Liked Songs vs. Streaming History ──────────")
    print(f"  Liked songs streamed at least once : {streamed:,}  ({streamed/total*100:.1f}%)")
    print(f"  Liked songs never streamed         : {never_played:,}  ({never_played/total*100:.1f}%)")

    # Most-streamed liked songs
    top = merged.sort_values("play_count", ascending=False).head(num)
    print(f"\n  Your most-streamed liked songs (top {num}):")
    print(f"  {'#':<4} {'Track':<45} {'Artist':<28} Plays")
    print("  " + "─" * 85)
    for i, (_, row) in enumerate(top.iterrows(), 1):
        t_name = str(row["track"])[:43]
        artist = str(row["artist"])[:26]
        print(f"  {i:<4} {t_name:<45} {artist:<28} {row['play_count']:,}")

    # Chart: top liked songs by stream count
    top_chart = merged.sort_values("play_count", ascending=False).head(num)
    fig, ax = plt.subplots(figsize=(13, 6))
    ax.bar(top_chart["track"].str[:30], top_chart["play_count"],
           color="mediumseagreen")
    ax.set(title=f"Your Most-Streamed Liked Songs (Top {num})",
           xlabel="Track", ylabel="Times Played")
    ax.tick_params(axis="x", labelrotation=75)
    plt.subplots_adjust(bottom=0.5)
    plt.tight_layout()
    plt.show()

    # Pie: streamed vs never played
    fig2, ax2 = plt.subplots(figsize=(7, 6))
    ax2.pie([streamed, never_played],
            labels=["Streamed at least once", "Never streamed"],
            autopct="%1.1f%%",
            colors=["mediumseagreen", "lightcoral"],
            explode=[0.05, 0.05], startangle=90, shadow=True)
    ax2.set_title("Liked Songs: Streamed vs. Never Played")
    plt.show()
