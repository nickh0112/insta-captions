# Instagram Reels Caption Extractor

Automatically extract captions from Instagram reels using a two-step approach:
1. **yt-dlp**: Grab existing Instagram auto-captions when available
2. **Whisper**: Generate captions using AI speech recognition for the rest

## Quick Start

### 1. Install Dependencies

```bash
# macOS / Linux
brew install ffmpeg yt-dlp        # or: pipx install yt-dlp
pip install -U openai-whisper     # ≈ git+https://github.com/openai/whisper.git
python -m pip install tqdm rich   # nice-to-have logging

# Or install all Python dependencies at once:
pip install -r requirements.txt
```

### 2. Setup Project

```bash
# Clone or create project directory
mkdir instagram-reels-captions && cd instagram-reels-captions

# Create required directories
mkdir -p subs tmp
```

### 3. Add Instagram URLs

Edit `reels.txt` and add one Instagram reel URL per line:

```txt
https://www.instagram.com/reels/ABC123/
https://www.instagram.com/reels/DEF456/
https://www.instagram.com/reels/GHI789/
```

### 4. Run Extraction

```bash
python run_all.py
```

## Project Structure

```
project/
├── reels.txt          # one IG URL per line
├── subs/              # final .srt files live here
├── tmp/               # scratch .m4a when we need ASR
├── downloaded.txt     # yt-dlp archive (skip dupes)
├── scrape_subs.py     # Step 1: yt-dlp extraction
├── fill_gaps.py       # Step 2: Whisper fallback
├── run_all.py         # Main runner script
└── requirements.txt   # Python dependencies
```

## How It Works

### Step 1: yt-dlp Extraction (`scrape_subs.py`)
- Uses `writeautomaticsub=True` to grab Instagram's auto-generated captions
- Skips video download (`skip_download=True`) to save bandwidth
- Converts to SRT format automatically
- Respects rate limits with `sleep_requests` and `max_downloads`

### Step 2: Whisper Fallback (`fill_gaps.py`)
- Downloads audio-only files (~1-3 MB/min) for reels without captions
- Uses OpenAI Whisper for speech-to-text conversion
- Generates SRT files with timestamps
- Cleans up temporary audio files automatically

## Usage Examples

### Run Complete Pipeline
```bash
python run_all.py
```

### Run Steps Individually
```bash
# Step 1: Extract existing captions
python scrape_subs.py

# Step 2: Fill gaps with Whisper
python fill_gaps.py
```

### Check Results
```bash
# Count generated captions
ls subs/*.srt | wc -l

# View a caption file
cat subs/EXAMPLE_REEL_ID.srt
```

## Configuration

### Whisper Model Selection
Edit `fill_gaps.py` to change the Whisper model:
- `"tiny"`: Fastest, least accurate
- `"base"`: Good balance
- `"small"`: Better accuracy
- `"medium"`: Best accuracy (default)
- `"large"`: Highest accuracy, slowest

### Rate Limiting
Adjust in `scrape_subs.py`:
```python
YDL_OPTS = {
    "sleep_requests": 1,      # Seconds between requests
    "max_downloads": 400,     # Max downloads per session
}
```

## Docker Support

Create a `Dockerfile`:

```dockerfile
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    ffmpeg \
    python3-pip \
    && pip install yt-dlp openai-whisper tqdm rich

COPY . /app
WORKDIR /app

CMD ["python3", "run_all.py"]
```

Run with:
```bash
docker build -t instagram-captions .
docker run -v $(pwd)/subs:/app/subs -v $(pwd)/downloaded.txt:/app/downloaded.txt instagram-captions
```

## Rate Limits & Legal Notes

- **Instagram Rate Limits**: ~200 Graph/API hits per hour per account/IP
- **Respect Copyright**: Only scrape public or permission-granted content
- **TOS Compliance**: Follow Instagram's Terms of Service
- **Compute Costs**: Whisper adds processing time (~real-time on CPU, 4-5× faster on GPU)

## Troubleshooting

### Common Issues

1. **"ffmpeg not found"**
   ```bash
   brew install ffmpeg  # macOS
   # or
   sudo apt install ffmpeg  # Ubuntu
   ```

2. **"yt-dlp not found"**
   ```bash
   pip install yt-dlp
   # or
   brew install yt-dlp  # macOS
   ```

3. **Whisper model download fails**
   ```bash
   # Check internet connection
   # Try smaller model: change "medium" to "tiny" in fill_gaps.py
   ```

4. **Rate limited by Instagram**
   - Increase `sleep_requests` in `scrape_subs.py`
   - Reduce `max_downloads`
   - Use VPN or different IP

### Performance Tips

- **GPU Acceleration**: Install CUDA for faster Whisper processing
- **Batch Processing**: Process in smaller batches to avoid rate limits
- **Parallel Processing**: Run multiple instances with different URL subsets

## License

This project is for educational purposes. Please respect Instagram's Terms of Service and applicable copyright laws. 