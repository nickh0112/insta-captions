#!/usr/bin/env python3
"""
Instagram Reels Caption Extractor - Main Runner
Runs both yt-dlp extraction and Whisper fallback
"""

import subprocess
import sys
from pathlib import Path

def check_dependencies():
    """Check if required tools are installed"""
    missing = []
    
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing.append("ffmpeg")
    
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing.append("yt-dlp")
    
    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        print("Install with: brew install ffmpeg yt-dlp")
        print("Or: pip install yt-dlp")
        return False
    
    return True

def main():
    """Run the complete caption extraction pipeline"""
    print("🎬 Instagram Reels Caption Extractor")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check if reels.txt exists
    if not Path("reels.txt").exists():
        print("❌ reels.txt not found. Please create it with Instagram URLs.")
        sys.exit(1)
    
    # Step 1: Extract existing captions with yt-dlp
    print("\n📥 Step 1: Extracting existing captions with yt-dlp...")
    try:
        # Import and run the function directly instead of subprocess
        from scrape_subs import run_batch
        run_batch("reels.txt")
        print("✅ Step 1 completed")
    except Exception as e:
        print(f"❌ Step 1 failed: {e}")
        sys.exit(1)
    
    # Step 2: Fill gaps with Whisper
    print("\n🎤 Step 2: Processing remaining reels with Whisper...")
    try:
        # Import and run the function directly instead of subprocess
        from fill_gaps import main as fill_gaps_main
        fill_gaps_main()
        print("✅ Step 2 completed")
    except Exception as e:
        print(f"❌ Step 2 failed: {e}")
        sys.exit(1)
    
    # Summary
    print("\n📊 Summary:")
    txt_files = list(Path("subs").glob("*.txt"))
    print(f"   Total transcripts generated: {len(txt_files)}")
    print(f"   Transcripts saved in: subs/")
    print(f"   Archive file: downloaded.txt")
    print(f"   Ready for content analysis!")

if __name__ == "__main__":
    main() 