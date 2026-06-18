# -*- coding: utf-8 -*-
"""
Batch transcriber: reads YouTube links from urls.txt (one per line) and converts
every one of them to text using the same pipeline as working_youtube_to_text.py.

- Lines starting with '#' or blank lines are ignored.
- A playlist link is automatically expanded into all of its videos.
- Videos that already have an output .txt are skipped (resume-friendly).
- One failure does not stop the batch; a summary is printed at the end.

Usage:
    python transcribe_all.py            # reads urls.txt
    python transcribe_all.py my_list.txt
"""

import os
import sys
import time

import yt_dlp

from working_youtube_to_text import WorkingYouTubeToText


def read_url_list(path):
    """Return non-empty, non-comment lines from the list file."""
    if not os.path.exists(path):
        return []
    urls = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            urls.append(line)
    return urls


def expand_playlists(urls):
    """Expand any playlist links into individual video URLs. Plain video links
    pass through unchanged. Order and duplicates-removal are preserved."""
    expanded = []
    seen = set()

    def add(u):
        if u and u not in seen:
            seen.add(u)
            expanded.append(u)

    flat_opts = {"extract_flat": "in_playlist", "quiet": True, "no_warnings": True}
    for url in urls:
        try:
            with yt_dlp.YoutubeDL(flat_opts) as ydl:
                info = ydl.extract_info(url, download=False)
        except Exception as e:
            print(f"⚠️  استخراج اطلاعات این لینک ممکن نشد، رد می‌شود: {url}\n   {e}")
            continue

        entries = info.get("entries") if isinstance(info, dict) else None
        if entries:
            for entry in entries:
                if not entry:
                    continue
                vid = entry.get("id")
                vurl = entry.get("url")
                if vurl and vurl.startswith("http"):
                    add(vurl)
                elif vid:
                    add(f"https://www.youtube.com/watch?v={vid}")
        else:
            add(url)
    return expanded


def already_done(converter, url):
    """Best-effort skip: if a .txt whose name matches this video's title exists."""
    try:
        video_id = converter.extract_video_id(url)
        if not video_id:
            return False
        flat_opts = {"quiet": True, "no_warnings": True, "skip_download": True}
        with yt_dlp.YoutubeDL(flat_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        title = info.get("title") or video_id
        base = converter._make_safe_basename(title, fallback=video_id, max_length=20)
        out = os.path.join(converter.output_dir, f"{base}.txt")
        return os.path.exists(out)
    except Exception:
        return False


def main():
    list_path = sys.argv[1] if len(sys.argv) > 1 else "urls.txt"
    raw_urls = read_url_list(list_path)
    if not raw_urls:
        print(f"❌ هیچ لینکی در «{list_path}» پیدا نشد.")
        print("   لینک‌های یوتیوب را (هر کدام در یک خط) داخل این فایل بگذارید.")
        return

    print(f"📋 {len(raw_urls)} ورودی از «{list_path}» خوانده شد. در حال باز کردن پلی‌لیست‌ها...")
    videos = expand_playlists(raw_urls)
    print(f"🎬 مجموعاً {len(videos)} ویدیو برای پردازش.\n")

    converter = WorkingYouTubeToText()

    ok, skipped, failed = [], [], []
    batch_start = time.time()

    for i, url in enumerate(videos, 1):
        print("=" * 60)
        print(f"[{i}/{len(videos)}] {url}")
        if already_done(converter, url):
            print("⏭️  قبلاً پردازش شده، رد می‌شود.")
            skipped.append(url)
            continue
        try:
            result = converter.transcribe_video(url)
            if result:
                ok.append(url)
            else:
                failed.append(url)
        except Exception as e:
            print(f"❌ خطا در پردازش این ویدیو: {e}")
            failed.append(url)

    total = time.time() - batch_start
    print("\n" + "=" * 60)
    print("📊 خلاصه‌ی پردازش انبوه:")
    print(f"  ✅ موفق:   {len(ok)}")
    print(f"  ⏭️  رد شده: {len(skipped)}")
    print(f"  ❌ ناموفق: {len(failed)}")
    print(f"  ⏱️  کل زمان: {total/60:.1f} دقیقه")
    if failed:
        print("\nلینک‌های ناموفق (می‌توانید دوباره اجرا کنید؛ موفق‌ها رد می‌شوند):")
        for u in failed:
            print(f"   - {u}")


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    main()
