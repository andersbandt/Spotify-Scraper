
# main.py
#   Interactive CLI for Spotify streaming history analysis.
#   Edit the two paths below, then run: python main.py

import os
import spotify_scraper
import spotify_analysis
import spotify_playlists
import spotify_library

# ── Configure your data paths here ────────────────────────────────────────────

# Directory containing your streaming history JSON files.
# Supports both Extended Streaming History (endsong_*.json) and
# basic Account Data history (StreamingHistory*.json) — auto-detected on load.
#STREAMING_HISTORY_DIR = "~/OneDrive/Backup/company_data_exports/Spotify/2023_06_21_spotify/my_spotify_data - Account Data/MyData/"
STREAMING_HISTORY_DIR = "~/OneDrive/Backup/company_data_exports/Spotify/2025_01_14_spotify/my_spotify_data/Spotify Extended Streaming History/"


# Full path to Playlist1.json from Spotify's "Account Data" export.
PLAYLIST_FILE = "~/OneDrive/Backup/company_data_exports/Spotify/2023_06_21_spotify/my_spotify_data - Account Data/MyData/Playlist1.json"


# Full path to YourLibrary.json from Spotify's "Account Data" export.
LIBRARY_FILE = "~/OneDrive/Backup/company_data_exports/Spotify/2023_06_21_spotify/my_spotify_data - Account Data/MyData/YourLibrary.json"

# Your local timezone for time-of-day charts (daytime_usage, listening_heatmap).
# Uses IANA timezone names: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
TIMEZONE = "America/Chicago"

# ─────────────────────────────────────────────────────────────────────────────

MENU = """
╔══════════════════════════════════════════════════════╗
║              Spotify Analysis Tool                   ║
╚══════════════════════════════════════════════════════╝

  ── Streaming History ───────────────────────────────
   1   Top songs by play count
   2   Top songs by total listening time
   3   Top artists by play count
   4   Top artists by total listening time
   5   Unique songs per top artist
   6   Unique artist ratio (pie chart)
   7   Unique song ratio (pie chart)
   8   Monthly listening distribution
   9   Hourly listening distribution
  10   Day-of-week × hour heatmap
  11   Songs played by day of week
  12   Weekday vs. weekend
  13   Songs played per day (scatter)
  14   Year-over-year comparison
  15   Cumulative listening time
  16   Skip rate analysis
  17   Listening summary stats

  ── Playlists ───────────────────────────────────────
  18   List all playlists
  19   View playlist tracks
  20   Export playlist to CSV
  21   Playlist stats summary

  ── Your Library (Liked Songs) ──────────────────────
  22   Library stats (total liked, top artists)
  23   Browse liked songs
  24   Liked songs you actually listen to most

  ── Other ───────────────────────────────────────────
   0   Run all streaming history analyses
   q   Quit
"""


def _prompt_int(prompt, default):
    """Prompt for an integer; return `default` on empty or invalid input."""
    raw = input(f"  {prompt} [default {default}]: ").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        print(f"  Invalid input — using {default}.")
        return default


def _require_playlists(playlists):
    """Print a helpful message and return False if playlists not loaded."""
    if playlists is None:
        print("\n  Playlist file not loaded.")
        print("  Set PLAYLIST_FILE in main.py to the path of your Playlist1.json.")
        return False
    return True


def _require_library(library):
    """Print a helpful message and return False if library not loaded."""
    if library is None:
        print("\n  Library file not loaded.")
        print("  Set LIBRARY_FILE in main.py to the path of your YourLibrary.json.")
        return False
    return True


def run_menu(sp_dt, playlists, library):
    while True:
        print(MENU)
        choice = input("  Enter choice: ").strip().lower()

        # ── streaming history ─────────────────────────────────────────────────
        if choice == "1":
            n = _prompt_int("Number of top songs", 20)
            spotify_analysis.top_songs(sp_dt, n, "Count")

        elif choice == "2":
            n = _prompt_int("Number of top songs", 20)
            spotify_analysis.top_songs(sp_dt, n, "ms_played")

        elif choice == "3":
            n = _prompt_int("Number of top artists", 20)
            spotify_analysis.top_artists(sp_dt, n, "Count")

        elif choice == "4":
            n = _prompt_int("Number of top artists", 20)
            spotify_analysis.top_artists(sp_dt, n, "ms_played")

        elif choice == "5":
            n = _prompt_int("Number of top artists", 20)
            spotify_analysis.uniq_song_from_artist(sp_dt, n)

        elif choice == "6":
            spotify_analysis.uniq_artist(sp_dt)

        elif choice == "7":
            spotify_analysis.uniq_song_pie(sp_dt)

        elif choice == "8":
            spotify_analysis.year_usage(sp_dt)

        elif choice == "9":
            spotify_analysis.daytime_usage(sp_dt)

        elif choice == "10":
            spotify_analysis.listening_heatmap(sp_dt)

        elif choice == "11":
            spotify_analysis.day_of_week(sp_dt)

        elif choice == "12":
            spotify_analysis.weekday_vs_weekend(sp_dt)

        elif choice == "13":
            spotify_analysis.max_song_day(sp_dt)

        elif choice == "14":
            spotify_analysis.yearly_comparison(sp_dt)

        elif choice == "15":
            spotify_analysis.cumulative_listening(sp_dt)

        elif choice == "16":
            threshold = _prompt_int("Skip threshold in seconds", 30)
            spotify_analysis.skip_analysis(sp_dt, skip_threshold_ms=threshold * 1000)

        elif choice == "17":
            spotify_analysis.listening_summary(sp_dt)

        # ── playlists ─────────────────────────────────────────────────────────
        elif choice == "18":
            if _require_playlists(playlists):
                spotify_playlists.list_playlists(playlists)

        elif choice == "19":
            if _require_playlists(playlists):
                spotify_playlists.list_playlists(playlists)
                name = input("  Enter playlist name or number: ").strip()
                spotify_playlists.show_playlist(playlists, name)

        elif choice == "20":
            if _require_playlists(playlists):
                spotify_playlists.list_playlists(playlists)
                name = input("  Enter playlist name or number: ").strip()
                out  = input("  Output file [default: playlist_export.csv]: ").strip()
                spotify_playlists.export_playlist(playlists, name, out or "playlist_export.csv")

        elif choice == "21":
            if _require_playlists(playlists):
                spotify_playlists.playlist_stats(playlists)

        # ── library ───────────────────────────────────────────────────────────
        elif choice == "22":
            if _require_library(library):
                spotify_library.library_stats(library)

        elif choice == "23":
            if _require_library(library):
                artist = input("  Filter by artist (leave blank for all): ").strip()
                spotify_library.browse_library(library, artist or None)

        elif choice == "24":
            if _require_library(library):
                n = _prompt_int("Number of top liked songs to show", 20)
                spotify_library.liked_vs_streamed(library, sp_dt, n)

        # ── other ─────────────────────────────────────────────────────────────
        elif choice == "0":
            n = _prompt_int("Number of top items for ranked charts", 20)
            print("\n  Running all streaming history analyses...\n")
            spotify_analysis.top_songs(sp_dt, n, "Count")
            spotify_analysis.top_songs(sp_dt, n, "ms_played")
            spotify_analysis.top_artists(sp_dt, n, "Count")
            spotify_analysis.top_artists(sp_dt, n, "ms_played")
            spotify_analysis.uniq_song_from_artist(sp_dt, n)
            spotify_analysis.uniq_artist(sp_dt)
            spotify_analysis.uniq_song_pie(sp_dt)
            spotify_analysis.year_usage(sp_dt)
            spotify_analysis.daytime_usage(sp_dt)
            spotify_analysis.listening_heatmap(sp_dt)
            spotify_analysis.day_of_week(sp_dt)
            spotify_analysis.weekday_vs_weekend(sp_dt)
            spotify_analysis.max_song_day(sp_dt)
            spotify_analysis.yearly_comparison(sp_dt)
            spotify_analysis.cumulative_listening(sp_dt)
            spotify_analysis.skip_analysis(sp_dt)

        elif choice in ("q", "quit", "exit"):
            print("\n  Goodbye!\n")
            break

        else:
            print("  Unknown option. Enter a number from the menu, or q to quit.")


if __name__ == "__main__":
    print("\nLoading streaming history...")
    sp_dt = spotify_scraper.extract_data(STREAMING_HISTORY_DIR)
    sp_dt = spotify_scraper.clean_data(sp_dt)
    sp_dt["datetime"] = sp_dt["datetime"].dt.tz_convert(TIMEZONE)
    print(f"  Loaded {len(sp_dt):,} streaming events (times shown in {TIMEZONE}).\n")
    spotify_analysis.listening_summary(sp_dt)

    playlists = None
    _playlist_path = os.path.expanduser(PLAYLIST_FILE) if PLAYLIST_FILE else ""
    if _playlist_path and os.path.exists(_playlist_path):
        print("Loading playlists...")
        playlists = spotify_playlists.load_playlists(_playlist_path)
    elif _playlist_path:
        print(f"  Warning: PLAYLIST_FILE path not found: {_playlist_path}")

    library = None
    _library_path = os.path.expanduser(LIBRARY_FILE) if LIBRARY_FILE else ""
    if _library_path and os.path.exists(_library_path):
        print("Loading library...")
        library = spotify_library.load_library(_library_path)
    elif _library_path:
        print(f"  Warning: LIBRARY_FILE path not found: {_library_path}")

    run_menu(sp_dt, playlists, library)
