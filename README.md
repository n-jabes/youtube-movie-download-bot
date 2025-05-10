
```markdown
# 🎬 TMDB to YouTube Downloader Bot (Multi-Language Support)

This Python script allows you to find and download full movies from YouTube based on TMDB metadata. It automatically finds the best matching video based on title, duration, and other criteria, then downloads it with your preferred audio language.

---

## 🛠️ Features

- 🔍 **Smart Movie Matching** - Finds full movies on YouTube using TMDB metadata
- 🎞️ **High-Quality Downloads** - Gets highest quality video and audio streams
- ⏱️ **Duration Matching** - Ensures video length matches TMDB runtime (±3 minutes)
- 🌍 **Multi-Language Support** - Prefers specified language, falls back to English
- 📂 **Organized Storage** - Creates structured directories for each download
- 🔄 **Multiple Download Modes**:
  - `merged`: Single file with video+audio
  - `separate`: Separate video, audio, and subtitle files
  - `both`: Tries separate first, falls back to merged
  - `check`: Only verifies language availability

---

## 📦 Installation

1. **Clone the repository**

```bash
git clone https://github.com/username/youtube-downloader-bot.git
cd youtube-downloader-bot
```

2. **Install dependencies**

```bash
pip install yt-dlp requests
```

> ℹ️ Ensure you're using Python 3.6+ and the correct Python environment

---

## 🚀 How to Use

### Basic Usage

```bash
python youtube_downloader.py TMDB_MOVIE_ID --lang LANGUAGE_CODE --mode MODE [--verbose]
```

### Parameters

- `TMDB_MOVIE_ID`: The TMDB movie ID (e.g., 155 for The Dark Knight)
- `--lang`: Preferred audio/subtitle language (default: `fr` for French)
- `--mode`: Download mode (`merged`, `separate`, `both`, or `check`)
- `--verbose` or `-v`: Show detailed matching and format information

### Sample Commands

#### Download The Dark Knight (ID 155) with French audio
```bash
python youtube_downloader.py 155 --lang fr --mode both --verbose
```

#### Check language availability for a movie
```bash
python youtube_downloader.py 155 --lang es --mode check
```

#### Download with English audio (separate streams)
```bash
python youtube_downloader.py 155 --lang en --mode separate
```

---

## 🧰 Output Example

### Successful Match and Download

```
✅ Fetched movie details from TMDB successfully

🎬 Movie Information:
  Title: The Dark Knight (The Dark Knight)
  Year: 2008
  Runtime: 152 minutes
  Certification: PG-13
  Genres: Action, Crime, Drama
  Directors: Christopher Nolan
  Main Actors: Christian Bale, Heath Ledger, Aaron Eckhart

🔍 Searching YouTube for best matching movie...
  Searching YouTube for: 'The Dark Knight 2008 full movie'

🏆 Best Match Found:
  Title: The Dark Knight (2008) Full Movie | HD Quality
  URL: https://www.youtube.com/watch?v=example123
  Duration: 152m 18s
  Match Score: 0.92/1.00

🎬 URL: https://www.youtube.com/watch?v=example123
🌍 Preferred Language: fr
🛠️ Mode: both

🎥 Title: The Dark Knight (2008) Full Movie | HD Quality
⏱️ Duration: 152m 18s

📊 Stream Selection:
  • Video: 137 (1080p)
  • Audio: 140 (Language: en) [fr not available]

🔽 Downloading separate video and audio streams...
✅ Video stream saved: The_Dark_Knight_2008_video.mp4
✅ Audio stream saved: The_Dark_Knight_2008_audio_en.m4a
✅ Subtitles downloaded

📁 All output saved to: Youtube_Bot_Downloads/The_Dark_Knight_2008
```

### Directory Structure

```
Youtube_Bot_Downloads/
└── The_Dark_Knight_2008/
    ├── The_Dark_Knight_2008_video.mp4
    ├── The_Dark_Knight_2008_audio_en.m4a
    ├── The_Dark_Knight_2008.fr.vtt
    ├── The_Dark_Knight_2008.en.vtt
    └── The_Dark_Knight_2008_merged.mp4 (if using 'both' mode)
```

---

## 🧠 How It Works

1. **TMDB Lookup**: Fetches movie details (title, year, runtime, etc.)
2. **YouTube Search**: Finds videos matching:
   - Title similarity
   - Duration (±3 minutes of TMDB runtime)
   - "Full movie" indicators
   - Release year match
3. **Scoring**: Rates matches (0.0-1.0) based on:
   - Title match (40%)
   - Duration match (30%)
   - "Full movie" in title (10%)
   - Year match (10%)
   - Official TMDB video (10%)
4. **Download**: Gets the best available match with preferred language

---

## ⚙️ Troubleshooting

- **No matches found**: Try a different TMDB ID or check if the movie exists on YouTube
- **Timeout errors**: Increase timeout in script or try again later
- **Language not available**: The script will automatically fallback to English
- **Low quality matches**: Use `--verbose` to see matching details

---

## 💬 Need Help?

Open an issue if you encounter problems or have suggestions for improvement!

---

Happy movie downloading! 🎥🍿
