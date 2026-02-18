
# spotify_analysis.py
#   Visualization and analysis functions for Spotify Extended Streaming History.
#   All functions accept the cleaned DataFrame produced by spotify_scraper.clean_data().
#
#   'type' parameter used throughout:
#       "Count"     - number of times played
#       "ms_played" - total milliseconds played (converted to hours in charts)

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import seaborn as sns


# ── Helpers ───────────────────────────────────────────────────────────────────

ARTIST_COL = "master_metadata_album_artist_name"
TRACK_COL  = "master_metadata_track_name"
MS_TO_HOURS = 2.77e-7   # multiply ms_played by this to get hours

_GREEN_PALETTE = "Greens_r"


def _bar_chart(ax, labels, values, title, xlabel, ylabel, color="mediumseagreen", rotate=75):
    ax.bar(labels, values, color=color)
    ax.set(title=title, xlabel=xlabel, ylabel=ylabel)
    ax.tick_params(axis="x", labelrotation=rotate)
    plt.tight_layout()


##############################################################################
####      ARTIST / SONG ANALYSIS                                          ####
##############################################################################

def top_songs(sp_df, num=20, type="Count"):
    """Bar chart of the top `num` songs by play count or total playtime."""
    grouped = (sp_df.groupby(TRACK_COL)[[type]]
                    .sum()
                    .sort_values(by=type, ascending=False)
                    .head(num))

    if type == "ms_played":
        values = grouped[type] * MS_TO_HOURS
        ylabel = "Hours Played"
        title  = f"Top {num} Songs by Listening Time"
    else:
        values = grouped[type]
        ylabel = "Play Count"
        title  = f"Top {num} Songs by Play Count"

    print(f"\nTop {min(num, 20)} songs ({type}):")
    print(grouped.head(20).to_string())

    fig, ax = plt.subplots(figsize=(max(14, num // 2), 6))
    _bar_chart(ax, grouped.index, values, title, "Song", ylabel)
    plt.subplots_adjust(bottom=0.55)
    plt.show()


def top_artists(sp_df, num=20, type="Count"):
    """Bar chart of the top `num` artists by play count or total playtime."""
    grouped = (sp_df.groupby(ARTIST_COL)[[type]]
                    .sum()
                    .sort_values(by=type, ascending=False)
                    .head(num))

    if type == "ms_played":
        values = grouped[type] * MS_TO_HOURS
        ylabel = "Hours Played"
        title  = f"Top {num} Artists by Listening Time"
    else:
        values = grouped[type]
        ylabel = "Play Count"
        title  = f"Top {num} Artists by Play Count"

    fig, ax = plt.subplots(figsize=(max(14, num // 2), 6))
    _bar_chart(ax, grouped.index, values, title, "Artist", ylabel)
    plt.subplots_adjust(bottom=0.45)
    plt.show()


def uniq_artist(sp_df):
    """Pie chart showing the ratio of unique vs. repeated artist plays."""
    unique_artists = sp_df[ARTIST_COL].nunique()
    total_artists  = sp_df[ARTIST_COL].count()

    unique_pct = unique_artists / total_artists * 100
    print(f"\nUnique artist percentage: {unique_pct:.1f}%")

    sizes  = [unique_artists, total_artists - unique_artists]
    labels = ["Unique Artists", "Repeated Artists"]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie(sizes, labels=labels, autopct="%1.1f%%",
           explode=[0.05, 0.05], startangle=180, shadow=True,
           colors=["mediumseagreen", "lightgray"])
    ax.set_title("Unique vs. Repeated Artist Plays")
    plt.show()


def uniq_song_from_artist(sp_df, num=20, type="Count"):
    """Bar chart: number of unique tracks per top-N artists."""
    top_artists = (sp_df.groupby(ARTIST_COL)[[type]]
                        .sum()
                        .sort_values(by=type, ascending=False)
                        .head(num)
                        .index.tolist())

    num_unique = []
    for artist in top_artists:
        songs = sp_df[sp_df[ARTIST_COL] == artist]
        num_unique.append(songs[TRACK_COL].nunique())

    fig, ax = plt.subplots(figsize=(max(14, num // 2), 6))
    _bar_chart(ax, top_artists, num_unique,
               f"Unique Songs from Top {num} Artists", "Artist",
               "Unique Songs", color="mediumseagreen")
    plt.subplots_adjust(bottom=0.45)
    plt.show()


##############################################################################
####      TIME-OF-DAY / WEEKLY PATTERNS                                   ####
##############################################################################

def daytime_usage(sp_df):
    """Histogram of listening activity by hour of day (0–23)."""
    df = sp_df.copy()
    df["hour"] = df["datetime"].dt.hour

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.histplot(df["hour"], bins=24, kde=True, color="mediumseagreen", ax=ax)
    ax.set_xticks(range(0, 24))
    ax.set(title="Listening Activity Throughout the Day",
           xlabel="Hour of Day (24-hour clock)",
           ylabel="Songs Played")
    plt.tight_layout()
    plt.show()


def listening_heatmap(sp_df):
    """Seaborn heatmap: songs played by day-of-week (rows) × hour (columns)."""
    df = sp_df.copy()
    df["hour"]        = df["datetime"].dt.hour
    df["day_of_week"] = df["datetime"].dt.day_name()

    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday",
                 "Friday", "Saturday", "Sunday"]

    pivot = (df.groupby(["day_of_week", "hour"])["Count"]
               .sum()
               .unstack(fill_value=0)
               .reindex(day_order))

    fig, ax = plt.subplots(figsize=(16, 5))
    sns.heatmap(pivot, cmap="Greens", ax=ax, linewidths=0.3,
                cbar_kws={"label": "Songs Played"})
    ax.set(title="Listening Activity: Day of Week vs. Hour of Day",
           xlabel="Hour of Day (0–23)",
           ylabel="")
    plt.tight_layout()
    plt.show()


##############################################################################
####      YEAR / LONG-TERM TRENDS                                         ####
##############################################################################

def year_usage(sp_df):
    """Horizontal count plot: songs played per calendar month (1–12)."""
    df = sp_df.copy()
    df["month"] = pd.DatetimeIndex(df["datetime"]).month

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.countplot(y=df["month"], ax=ax, color="mediumseagreen",
                  order=range(1, 13))
    ax.set(title="Average Spotify Usage Across a Year",
           xlabel="Songs Played", ylabel="Month (1–12)")
    plt.tight_layout()
    plt.show()


def yearly_comparison(sp_df):
    """Side-by-side bar charts: songs played and hours listened per year."""
    df = sp_df.copy()
    df["year"] = df["datetime"].dt.year

    yearly = (df.groupby("year")
                .agg(plays=("Count", "sum"),
                     hours=("ms_played", lambda x: x.sum() * MS_TO_HOURS))
                .reset_index())

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    ax1.bar(yearly["year"].astype(str), yearly["plays"], color="mediumseagreen")
    ax1.set(title="Songs Played per Year", xlabel="Year", ylabel="Play Count")

    ax2.bar(yearly["year"].astype(str), yearly["hours"], color="seagreen")
    ax2.set(title="Hours Listened per Year", xlabel="Year", ylabel="Hours")

    plt.tight_layout()
    plt.show()


def max_song_day(sp_df):
    """Scatter plot of songs played per day, with mean line."""
    df = sp_df.copy()
    df["date"] = df["datetime"].dt.date

    daily = (df.groupby("date")[["Count"]]
               .sum()
               .sort_values(by="Count", ascending=False))

    print("\nDays with most songs played:")
    print(daily.head(5).to_string())

    fig, ax = plt.subplots(figsize=(15, 6))
    ax.scatter(daily.index, daily["Count"], color="mediumseagreen",
               s=10, alpha=0.6)
    ax.axhline(daily["Count"].mean(), linestyle="--", color="red",
               label=f"Mean: {daily['Count'].mean():.1f}")
    ax.set(title="Songs Played per Day Over Time",
           xlabel="Date", ylabel="Songs Played")
    ax.legend()
    plt.tight_layout()
    plt.show()


def cumulative_listening(sp_df):
    """Line chart of cumulative hours listened over the entire dataset."""
    df = sp_df.sort_values("datetime").copy()
    df["cumulative_hours"] = df["ms_played"].cumsum() * MS_TO_HOURS

    fig, ax = plt.subplots(figsize=(15, 6))
    ax.plot(df["datetime"], df["cumulative_hours"],
            color="mediumseagreen", linewidth=1)
    ax.fill_between(df["datetime"], df["cumulative_hours"],
                    alpha=0.25, color="mediumseagreen")
    ax.set(title="Cumulative Listening Time Over All Time",
           xlabel="Date", ylabel="Total Hours Listened")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda x, _: f"{int(x):,} h"))
    plt.tight_layout()
    plt.show()


##############################################################################
####      BEHAVIOR ANALYSIS                                               ####
##############################################################################

def skip_analysis(sp_df, skip_threshold_ms=30_000):
    """
    Two-panel figure:
      Left  — pie chart of skip rate (plays where ms_played < threshold).
      Right — horizontal bar chart of most-frequently skipped songs.

    Default threshold is 30 seconds (30,000 ms).
    """
    df = sp_df.copy()
    df["skipped"] = df["ms_played"] < skip_threshold_ms

    skipped_count = int(df["skipped"].sum())
    played_count  = int((~df["skipped"]).sum())
    total         = skipped_count + played_count

    print(f"\nSkip analysis (threshold: {skip_threshold_ms // 1000}s):")
    print(f"  Played : {played_count:,}  ({played_count / total * 100:.1f}%)")
    print(f"  Skipped: {skipped_count:,}  ({skipped_count / total * 100:.1f}%)")

    top_skipped = (df[df["skipped"]]
                   .groupby(TRACK_COL)["Count"]
                   .sum()
                   .sort_values(ascending=False)
                   .head(15))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    ax1.pie([played_count, skipped_count],
            labels=["Played", f"Skipped (< {skip_threshold_ms // 1000}s)"],
            autopct="%1.1f%%",
            colors=["mediumseagreen", "lightcoral"],
            explode=[0.05, 0.05], startangle=90, shadow=True)
    ax1.set_title("Skip Rate")

    ax2.barh(top_skipped.index[::-1], top_skipped.values[::-1],
             color="lightcoral")
    ax2.set(title="Most Frequently Skipped Songs",
            xlabel="Skip Count", ylabel="")
    ax2.tick_params(axis="y", labelsize=8)

    plt.tight_layout()
    plt.show()


##############################################################################
####      SUMMARY & ADDITIONAL VIEWS  (stolen from Spotify_Wrapped.ipynb) ####
##############################################################################

def listening_summary(sp_df):
    """Print a one-screen stats dashboard for the loaded dataset."""
    total_hours   = sp_df["ms_played"].sum() * MS_TO_HOURS
    first_date    = sp_df["datetime"].min()
    last_date     = sp_df["datetime"].max()
    days_span     = max((last_date - first_date).days, 1)
    avg_per_day   = len(sp_df) / days_span
    unique_artists = sp_df[ARTIST_COL].nunique()
    unique_tracks  = sp_df[TRACK_COL].nunique()

    print()
    print("  ╔══════════════════════════════════════════════╗")
    print("  ║           Your Listening at a Glance        ║")
    print("  ╠══════════════════════════════════════════════╣")
    print(f"  ║  Date range    {str(first_date.date())!s:>10} → {str(last_date.date())!s:<10}  ║")
    print(f"  ║  Span          {days_span:>10,} days                  ║")
    print(f"  ║  Total streams {len(sp_df):>10,}                      ║")
    print(f"  ║  Total hours   {total_hours:>10,.1f} h                  ║")
    print(f"  ║  Avg songs/day {avg_per_day:>10.1f}                      ║")
    print(f"  ║  Unique artists{unique_artists:>10,}                      ║")
    print(f"  ║  Unique tracks {unique_tracks:>10,}                      ║")
    print("  ╚══════════════════════════════════════════════╝")
    print()


def uniq_song_pie(sp_df):
    """Pie chart: unique vs. repeated song plays (mirrors uniq_artist for tracks)."""
    unique_songs = sp_df[TRACK_COL].nunique()
    total_songs  = sp_df[TRACK_COL].count()

    print(f"\n  Unique song percentage: {unique_songs / total_songs * 100:.1f}%")

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie([unique_songs, total_songs - unique_songs],
           labels=["Unique Songs", "Repeated Songs"],
           autopct="%1.1f%%",
           explode=[0.05, 0.05], startangle=180, shadow=True,
           colors=["mediumseagreen", "lightgray"])
    ax.set_title("Unique vs. Repeated Song Plays")
    plt.show()


def day_of_week(sp_df):
    """Bar chart of songs played by day of week (Monday → Sunday)."""
    df = sp_df.copy()
    df["day_name"] = df["datetime"].dt.day_name()

    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday",
                 "Friday", "Saturday", "Sunday"]

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.countplot(x=df["day_name"], order=day_order,
                  color="mediumseagreen", ax=ax)
    ax.set(title="Songs Played by Day of Week",
           xlabel="", ylabel="Songs Played")
    plt.tight_layout()
    plt.show()


def weekday_vs_weekend(sp_df):
    """Side-by-side bar charts comparing weekday vs. weekend listening."""
    df = sp_df.copy()
    df["is_weekend"] = df["datetime"].dt.day_name().isin(["Saturday", "Sunday"])

    summary = (df.groupby("is_weekend")["Count"]
                 .sum()
                 .reset_index())
    summary["label"] = summary["is_weekend"].map({False: "Weekday", True: "Weekend"})
    summary["pct"]   = summary["Count"] / summary["Count"].sum() * 100

    for _, row in summary.iterrows():
        print(f"  {row['label']}: {int(row['Count']):,}  ({row['pct']:.1f}%)")

    colors = ["steelblue", "mediumseagreen"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    ax1.bar(summary["label"], summary["Count"], color=colors)
    ax1.set(title="Weekday vs. Weekend (Count)", ylabel="Songs Played")

    ax2.bar(summary["label"], summary["pct"], color=colors)
    ax2.set(title="Weekday vs. Weekend (%)", ylabel="Percentage")
    ax2.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))

    plt.tight_layout()
    plt.show()
