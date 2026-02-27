
# spotify_playlists.py
#   Functions for loading and displaying Spotify playlist data from the
#   "Account Data" export (Playlist1.json).
#
#   Playlist1.json structure:
#   {
#     "playlists": [
#       {
#         "name": "...",
#         "lastModifiedDate": "YYYY-MM-DD",
#         "items": [
#           {
#             "track":      { "trackName", "artistName", "albumName", "trackUri" },
#             "episode":    { "episodeName", "showName", "episodeUri" },  # or null
#             "localTrack": ...,                                           # or null
#             "addedDate":  "YYYY-MM-DD"
#           }
#         ],
#         "description": "...",
#         "numberOfFollowers": 0
#       }
#     ]
#   }

import json
import os
import pandas as pd


def load_playlists(file_path):
    """
    Load Playlist1.json from a Spotify account data export.
    Returns the list of playlist dicts, or raises FileNotFoundError.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Playlist file not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    playlists = data.get("playlists", [])
    print(f"Loaded {len(playlists)} playlists.")
    return playlists


def list_playlists(playlists):
    """Print a numbered table of all playlists with track counts."""
    print(f"\n  {'#':<5} {'Playlist Name':<42} {'Tracks':<8} Last Modified")
    print("  " + "─" * 70)
    for i, pl in enumerate(playlists, 1):
        name     = str(pl.get("name", "Unnamed"))[:40]
        tracks   = len(pl.get("items", []))
        modified = pl.get("lastModifiedDate", "Unknown")
        print(f"  {i:<5} {name:<42} {tracks:<8} {modified}")
    print()


def show_playlist(playlists, identifier):
    """
    Print all tracks in a playlist.
    `identifier` can be a playlist number (1-based) or a name (case-insensitive).
    """
    pl = _find_playlist(playlists, identifier)
    if pl is None:
        print(f"  Playlist '{identifier}' not found. Use list_playlists() to see available playlists.")
        return

    items = pl.get("items", [])
    print(f"\n  Playlist : {pl.get('name', 'Unnamed')}")
    desc = pl.get("description", "").strip()
    if desc:
        print(f"  Desc     : {desc}")
    print(f"  Tracks   : {len(items)}")
    print(f"  Modified : {pl.get('lastModifiedDate', 'Unknown')}")
    print()
    print(f"  {'#':<5} {'Track':<45} {'Artist':<30} Added")
    print("  " + "─" * 90)

    for i, item in enumerate(items, 1):
        track   = item.get("track") or {}
        episode = item.get("episode") or {}
        added   = item.get("addedDate", "")

        if track:
            t_name = str(track.get("trackName",  ""))[:43]
            artist = str(track.get("artistName", ""))[:28]
        elif episode:
            t_name = str(episode.get("episodeName", ""))[:43]
            artist = str(episode.get("showName",    ""))[:28]
        else:
            t_name = "(local / unknown)"
            artist = ""

        print(f"  {i:<5} {t_name:<45} {artist:<30} {added}")
    print()


def export_playlist(playlists, identifier, output_path="playlist_export.csv"):
    """
    Export a playlist's tracks to a CSV file.
    `identifier` can be a playlist number (1-based) or a name (case-insensitive).
    """
    pl = _find_playlist(playlists, identifier)
    if pl is None:
        print(f"  Playlist '{identifier}' not found.")
        return

    rows = []
    for item in pl.get("items", []):
        track   = item.get("track") or {}
        episode = item.get("episode") or {}

        if track:
            rows.append({
                "type":       "track",
                "name":       track.get("trackName",  ""),
                "artist":     track.get("artistName", ""),
                "album":      track.get("albumName",  ""),
                "uri":        track.get("trackUri",   ""),
                "added_date": item.get("addedDate",   ""),
            })
        elif episode:
            rows.append({
                "type":       "episode",
                "name":       episode.get("episodeName", ""),
                "artist":     episode.get("showName",    ""),
                "album":      "",
                "uri":        episode.get("episodeUri",  ""),
                "added_date": item.get("addedDate",      ""),
            })

    df = pd.DataFrame(rows, columns=["type", "name", "artist", "album", "uri", "added_date"])
    df.to_csv(output_path, index=False)
    print(f"  Exported {len(rows)} tracks to '{output_path}'")


def playlist_stats(playlists):
    """Print a summary: total playlists, total tracks, and top contributors."""
    total_tracks = sum(len(pl.get("items", [])) for pl in playlists)
    print(f"\n  Total playlists : {len(playlists)}")
    print(f"  Total tracks    : {total_tracks:,}")

    # Longest playlists
    sorted_pl = sorted(playlists, key=lambda p: len(p.get("items", [])), reverse=True)
    print(f"\n  Longest playlists:")
    for pl in sorted_pl[:5]:
        print(f"    {len(pl.get('items', [])):>4} tracks — {pl.get('name', 'Unnamed')}")
    print()


def playlist_diff(old_playlists, new_playlists, identifier):
    """
    Compare a playlist between two exports and print what was added and dropped.
    Matches tracks by trackUri; falls back to 'artist||trackName' for local tracks.
    """
    # Resolve number/name against the new (displayed) list first, then match
    # the same playlist by name in the old list so ordering differences don't
    # cause a mismatch.
    new_pl = _find_playlist(new_playlists, identifier)
    if new_pl is None:
        print(f"  Playlist '{identifier}' not found in new export.")
        return

    playlist_name = new_pl.get("name", "")
    old_pl = _find_playlist(old_playlists, playlist_name)
    if old_pl is None:
        print(f"  Playlist '{playlist_name}' not found in old export (may not have existed yet).")
        return

    def _key(item):
        track = item.get("track") or {}
        uri = track.get("trackUri", "").strip()
        if uri:
            return uri
        return f"{track.get('artistName', '')}||{track.get('trackName', '')}"

    old_map = {_key(i): i for i in old_pl.get("items", []) if i.get("track")}
    new_map = {_key(i): i for i in new_pl.get("items", []) if i.get("track")}

    added_keys   = sorted(set(new_map) - set(old_map), key=lambda k: new_map[k].get("addedDate", ""))
    dropped_keys = sorted(set(old_map) - set(new_map), key=lambda k: old_map[k].get("addedDate", ""))
    kept         = len(set(old_map) & set(new_map))

    print(f"\n  Playlist diff: {old_pl.get('name', identifier)}")
    print(f"  Old  ({old_pl.get('lastModifiedDate', '?')}) : {len(old_map)} tracks")
    print(f"  New  ({new_pl.get('lastModifiedDate', '?')}) : {len(new_map)} tracks")
    print(f"  Added: {len(added_keys)}   Dropped: {len(dropped_keys)}   Unchanged: {kept}")

    if added_keys:
        print(f"\n  ── Added ({len(added_keys)}) " + "─" * 55)
        print(f"  {'Track':<45} {'Artist':<30} Date added")
        print("  " + "─" * 87)
        for k in added_keys:
            t = new_map[k].get("track", {})
            print(f"  {str(t.get('trackName',''))[:43]:<45} "
                  f"{str(t.get('artistName',''))[:28]:<30} "
                  f"{new_map[k].get('addedDate','')}")

    if dropped_keys:
        print(f"\n  ── Dropped ({len(dropped_keys)}) " + "─" * 53)
        print(f"  {'Track':<45} {'Artist':<30} Was added")
        print("  " + "─" * 87)
        for k in dropped_keys:
            t = old_map[k].get("track", {})
            print(f"  {str(t.get('trackName',''))[:43]:<45} "
                  f"{str(t.get('artistName',''))[:28]:<30} "
                  f"{old_map[k].get('addedDate','')}")

    print()


# ── Internal helpers ──────────────────────────────────────────────────────────

def _find_playlist(playlists, identifier):
    """
    Find a playlist by 1-based index (int or numeric string) or name (case-insensitive).
    Returns the playlist dict or None.
    """
    # Try numeric index
    try:
        idx = int(str(identifier).strip()) - 1
        if 0 <= idx < len(playlists):
            return playlists[idx]
    except (ValueError, TypeError):
        pass

    # Try exact name match (case-insensitive)
    name_lower = str(identifier).lower()
    for pl in playlists:
        if pl.get("name", "").lower() == name_lower:
            return pl

    # Try partial name match as fallback
    matches = [pl for pl in playlists if name_lower in pl.get("name", "").lower()]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        print(f"  Multiple playlists match '{identifier}':")
        for pl in matches:
            print(f"    - {pl.get('name')}")
        return None

    return None
