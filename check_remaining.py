# -*- coding: utf-8 -*-
"""Prints the number of videos that still have no transcript, across the list
files given as arguments (default: urls.txt queue_next.txt). Reuses
transcribe_all's own logic so the answer matches what the batch would do.
Used by the master scripts to decide when to stop retrying."""
import sys

try:
    from transcribe_all import read_url_list, expand_playlists, already_done
    from working_youtube_to_text import WorkingYouTubeToText

    lists = sys.argv[1:] or ["urls.txt", "queue_next.txt"]
    conv = WorkingYouTubeToText()
    urls = []
    for p in lists:
        urls += read_url_list(p)
    videos = expand_playlists(urls)
    seen = set()
    uniq = [u for u in videos if not (u in seen or seen.add(u))]
    missing = sum(0 if already_done(conv, u) else 1 for u in uniq)
    print(missing)
except Exception as e:
    sys.stderr.write(f"check_remaining error: {e}\n")
    print(-1)
