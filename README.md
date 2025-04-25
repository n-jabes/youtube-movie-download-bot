# 🎬 YouTube Video & Audio Downloader Bot (Multi-Language Support)

This Python script allows you to download videos and audio streams separately from YouTube at the highest available quality. It supports downloading audio in a preferred language (e.g., French 🇫🇷), and falls back to English if the preferred language is unavailable.

Perfect for building a **local movie or series database** using YouTube content—especially from sources like The Movie Database (TMDb) API.

---

## 🛠️ Features

- 🎞️ Downloads highest quality **video and audio streams** separately.
- 🌍 Audio language preference with automatic fallback to English.
- 📁 Downloads are saved in a structured `Youtube_Bot_Downloads/` directory.
- 📂 Each download gets its own subfolder with a clean title-based name.
- 📝 Captions (subtitles) downloaded in preferred language and English.
- 🧪 **Language availability check mode** to verify audio/subtitle availability without downloading.
- 🔍 Verbose mode for detailed format information.
- 🔄 **Four download modes**:
  - `merged`: Downloads and merges video + audio into one file
  - `separate`: Downloads video, audio, and subtitles as separate files
  - `both`: Tries both methods (separate first, then merged if needed)
  - `check`: Only checks language availability without downloading anything

---

## 📦 Installation

1. **Clone the repository**

```bash
git clone https://github.com/username/youtube-downloader-bot.git
cd youtube-downloader-bot
```

2. **Install dependencies**

```bash
pip install yt-dlp
```

> ⚠️ If you face issues during or after installation, check the Python interpreter you're using. Run:
>
> ```bash
> where python
> ```
> Ensure you're installing packages for the correct Python version.

---

## 🚀 How to Use

### Basic Usage

```bash
python youtube_downloader.py "VIDEO_URL" --lang LANGUAGE_CODE --mode MODE [--verbose]
```

### Parameters

- `VIDEO_URL`: The YouTube video URL to download
- `--lang`: Preferred audio/subtitle language code (default: `fr` for French)
- `--mode`: Download mode (`merged`, `separate`, `both`, or `check`)
- `--verbose` or `-v`: Show detailed output including available formats

### 🧪 Sample Test Commands

You can test the bot using one of the following sample videos that have **multi-language audio**:

#### Basic Download (French audio preferred)

```bash
python youtube_downloader.py "https://www.youtube.com/watch?v=2isYuQZMbdU" --lang fr --mode merged
```

#### Download separate streams with verbose output

```bash
python youtube_downloader.py "https://www.youtube.com/watch?v=2isYuQZMbdU" --lang fr --mode separate --verbose
```

#### Try both methods (separate first, then merged)

```bash
python youtube_downloader.py "https://www.youtube.com/watch?v=2isYuQZMbdU" --lang fr --mode both --verbose
```

#### Check language availability only (no download)

```bash
python youtube_downloader.py "https://www.youtube.com/watch?v=2isYuQZMbdU" --lang fr --mode check
```

#### With English as preferred language

```bash
python youtube_downloader.py "https://www.youtube.com/watch?v=9bZkp7q19f0" --lang en --mode merged
```

---

## 🧰 Output Example

### Download Mode Output

```
🎬 URL: https://www.youtube.com/watch?v=2isYuQZMbdU
🌍 Preferred Language: fr
🛠️ Mode: both

🎥 Title: I Gave My 100,000,000th Subscriber An Island
⏱️ Duration: 15m 30s

📊 Stream Selection:
  • Video: 137 (1080p)
  • Audio: 140-14 (Language: fr)

🔽 Downloading separate video and audio streams...
✅ Audio stream saved: I_Gave_My_100_000_000th_Subscriber_An_Is_audio_fr.m4a
✅ Subtitles downloaded (if available)

📁 All output saved to: Youtube_Bot_Downloads\I_Gave_My_100_000_000th_Subscriber_An_Is
```

### Check Mode Output

```
🔍 Checking language availability for https://www.youtube.com/watch?v=2isYuQZMbdU
🌍 Preferred Language: fr
✅ Audio in fr: True
✅ Subtitles in fr: True
```

## 📁 Directory Structure

```
Youtube_Bot_Downloads/
└── I_Gave_My_100_000_000th_Subscriber_An_Is/
    ├── I_Gave_My_100_000_000th_Subscriber_An_Is_video.mp4
    ├── I_Gave_My_100_000_000th_Subscriber_An_Is_audio_fr.m4a
    ├── I_Gave_My_100_000_000th_Subscriber_An_Is.fr.vtt
    ├── I_Gave_My_100_000_000th_Subscriber_An_Is.en.vtt
    └── I_Gave_My_100_000_000th_Subscriber_An_Is_merged.mp4 (if using 'both' mode)
```

---

## 🧠 Notes

- This script uses `yt-dlp`, a more up-to-date fork of `youtube-dl` that handles modern YouTube formats better.
- For large videos, downloads may take time or timeout. Consider using a stable internet connection.
- Some videos might not have separate audio streams in all languages. The script will fall back to the best available option.
- To upgrade yt-dlp:
  ```bash
  pip install --upgrade yt-dlp
  ```

---

## ⚙️ Troubleshooting

- **Timeouts**: If you experience timeouts with large videos, try using the merged mode or increase your connection stability.
- **Format Issues**: Use `--verbose` to see all available formats for troubleshooting.
- **Language Not Available**: Use `--mode check` to verify if your preferred language is available before downloading.

---

## 💬 Questions?

If you encounter issues or want to suggest improvements, feel free to open an issue or reach out!

---

Happy downloading! 📥