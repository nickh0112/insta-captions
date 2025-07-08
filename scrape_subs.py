#!/usr/bin/env python3
"""
Instagram Reels Caption Extractor - Step 1
Uses yt-dlp to grab any captions Instagram already made
"""

from yt_dlp import YoutubeDL
from pathlib import Path

SUB_DIR = Path("subs")
SUB_DIR.mkdir(exist_ok=True)

YDL_OPTS = {
    "skip_download": True,
    "writeautomaticsub": True,     # <-- auto-generated captions
    "subtitleslangs": ["en"],
    "convert_subs": "srt",
    "outtmpl": {"subtitle": str(SUB_DIR / "%(id)s.%(ext)s")},
    "download_archive": "downloaded.txt",
    "sleep_requests": 1,
    "max_downloads": 400,          # stay under IG soft-limit
}

def run_batch(url_file: str):
    """Process all URLs in the file using yt-dlp"""
    with open(url_file) as f, YoutubeDL(YDL_OPTS) as ydl:
        urls = [u.strip() for u in f if u.strip() and not u.startswith('#')]
        print(f"Processing {len(urls)} URLs...")
        ydl.download(urls)

if __name__ == "__main__":
    run_batch("reels.txt") 