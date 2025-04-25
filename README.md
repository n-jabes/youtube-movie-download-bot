

```markdown
# 🎬 YouTube Video & Audio Downloader Bot (Multi-Language Support)

This Python script allows you to download videos and audio streams separately from YouTube at the highest available quality. It supports downloading audio in a preferred language (e.g., French 🇫🇷), and falls back to English if the preferred language is unavailable.

Perfect for building a **local movie or series database** using YouTube content—especially from sources like The Movie Database (TMDb) API.

---

## 🛠️ Features

- 🎞️ Downloads highest quality **video and audio streams** separately.
- 🌍 Audio language preference (e.g., French) with automatic fallback to English.
- 📁 Downloads are saved in a structured `Youtube_Bot_Downloads/` directory.
- 🧠 Automatically names files based on YouTube titles.
- 🧾 Logging with details like:
  - Video title
  - Size
  - Language
  - Duration

---

## 📦 Installation

1. **Clone the repository**

```bash
git clone https://github.com/n-jabes/youtube-movie-download-bot.git youtube-downloader-bot
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

### 🧪 Test with a sample video

You can test the bot using one of the following sample videos that have **multi-language audio**:

#### ✅ 1. MrBeast video (has French audio)

```bash
python youtube_bot.py "https://www.youtube.com/watch?v=2isYuQZMbdU" fr
```

#### 🔢 2. Counting puzzle (surprisingly complex logic)

```bash
python youtube_bot.py "https://www.youtube.com/watch?v=9bZkp7q19f0" en
```

This will:
- Try to download the video in the preferred language (`fr` or `en`).
- Save it as `Youtube_Bot_Downloads/<title>.mp4`.

---

## 🧰 Output Example

```
🎬 Processing URL: https://www.youtube.com/watch?v=2isYuQZMbdU
🌍 Preferred audio language: fr
✅ Video Title: I Gave My 100,000,000th Subscriber An Island
🎥 Duration: 17m 32s
🔈 Language: fr
💾 Size: 140.2 MB
⬇️ Downloading video [...]+ audio [...]
✅ Done! Saved to: Youtube_Bot_Downloads/I_Gave_My_100,000,000th_Subscriber_An_Island.mp4
```

---

## 🧠 Notes

- This script uses `yt-dlp`, a more up-to-date fork of `youtube-dl` that handles modern YouTube formats better.
- If you don’t have `yt-dlp` globally accessible, use the `--user` flag during installation or ensure your PATH is correctly set.
- To upgrade:
  ```bash
  pip install --upgrade yt-dlp
  ```

---

## 💬 Questions?

If you encounter issues or want to suggest improvements, feel free to open an issue or reach out!

---

Happy downloading! 📥
```

---

Let me know if you want to add badges, license info, or usage in other languages like Japanese or Spanish. You’re crushing it!
