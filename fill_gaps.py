#!/usr/bin/env python3
"""
Instagram Reels Caption Extractor - Step 2
Fallback: do your own ASR where no .srt exists
"""

import subprocess
import shutil
from pathlib import Path
import whisper
from tqdm import tqdm

SUB_DIR = Path("subs")
TMP_DIR = Path("tmp")
TMP_DIR.mkdir(exist_ok=True)
MODEL = whisper.load_model("medium")   # GPU? pick tiny/base/small otherwise

def ensure_transcript(url: str):
    """Ensure we have a transcript for the given URL"""
    short = url.rstrip("/").split("/")[-1]
    txt_path = SUB_DIR / f"{short}.txt"
    
    if txt_path.exists():
        print(f"✅ {short}: Transcript already exists")
        return  # Already processed ✅

    print(f"🔄 {short}: Processing with Whisper...")

    # 1️⃣ audio-only download (~1-3 MB/min)
    audio = TMP_DIR / f"{short}.m4a"
    if not audio.exists():
        try:
            subprocess.run(
                ["yt-dlp", "-f", "ba", "-o", str(audio), url], 
                check=True, capture_output=True, text=True
            )
        except subprocess.CalledProcessError as e:
            print(f"❌ {short}: Failed to download audio - {e}")
            return

    # 2️⃣ whisper → .txt (clean text for analysis)
    try:
        # Use the newer Whisper API
        result = MODEL.transcribe(
            str(audio), 
            language="en",
            fp16=False  # turn off if CPU-only
        )
        
        # Extract clean text for analysis
        full_text = result["text"].strip()
        
        # Write clean text file for content analysis
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(f"URL: {url}\n")
            f.write(f"Transcribed: {full_text}\n\n")
            
            # Also include segmented text for more detailed analysis
            f.write("=== SEGMENTED TRANSCRIPT ===\n")
            for i, segment in enumerate(result["segments"], 1):
                start_time = int(segment["start"])
                end_time = int(segment["end"])
                text = segment["text"].strip()
                
                # Convert to readable time format
                start_minutes = start_time // 60
                start_seconds = start_time % 60
                end_minutes = end_time // 60
                end_seconds = end_time % 60
                
                f.write(f"[{start_minutes:02d}:{start_seconds:02d}-{end_minutes:02d}:{end_seconds:02d}] {text}\n")
        
        print(f"✅ {short}: Text transcript created for analysis")
    except Exception as e:
        print(f"❌ {short}: Whisper failed - {e}")
    finally:
        # Clean up audio file
        audio.unlink(missing_ok=True)

def main():
    """Process all URLs that don't have captions yet"""
    urls = []
    with open("reels.txt") as f:
        urls = [u.strip() for u in f if u.strip() and not u.startswith('#')]
    
    print(f"Processing {len(urls)} URLs with Whisper fallback...")
    
    for url in tqdm(urls, desc="Processing reels"):
        ensure_transcript(url)

if __name__ == "__main__":
    main() 