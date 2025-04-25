import sys
import os
import re
from yt_dlp import YoutubeDL

def sanitize_filename(name):
    return re.sub(r'[^a-zA-Z0-9_]+', '_', name)[:40].strip('_')

def download_video_audio(url, preferred_lang='fr'):
    print(f"🎬 Processing URL: {url}")
    print(f"🌍 Preferred audio language: {preferred_lang}")

    # Base download directory
    base_dir = "Youtube_Bot_Downloads"
    os.makedirs(base_dir, exist_ok=True)

    # Get info first
    ydl_opts = {'quiet': True, 'skip_download': True}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    title = info.get('title', 'video')
    folder_name = sanitize_filename(title)
    download_dir = os.path.join(base_dir, folder_name)
    os.makedirs(download_dir, exist_ok=True)

    duration = info.get('duration', 0)
    duration_min = f"{duration // 60}m {duration % 60}s"
    formats = info.get('formats', [])
    subtitles = info.get('subtitles', {})

    best_video = None
    preferred_audio = None
    fallback_audio = None

    for f in formats:
        if f.get('vcodec') != 'none' and f.get('acodec') == 'none':
            if not best_video or f.get('height', 0) > best_video.get('height', 0):
                best_video = f
        elif f.get('acodec') != 'none' and f.get('vcodec') == 'none':
            lang = f.get('language') or ''
            if preferred_lang.lower() in lang.lower():
                preferred_audio = f if not preferred_audio else preferred_audio
            elif 'en' in lang.lower():
                fallback_audio = f if not fallback_audio else fallback_audio

    selected_audio = preferred_audio or fallback_audio
    if not best_video or not selected_audio:
        print("⚠️ Couldn't find separate streams. Downloading best available...")
        ydl_opts = {
            'outtmpl': os.path.join(download_dir, f"%(title)s.%(ext)s"),
            'writesubtitles': True,
            'subtitleslangs': [preferred_lang, 'en'],
            'quiet': False
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"✅ Downloaded to: {download_dir}")
        return

    video_fmt = best_video['format_id']
    audio_fmt = selected_audio['format_id']
    lang_code = selected_audio.get('language', 'unknown')
    size = best_video.get('filesize_approx') or best_video.get('filesize') or 0
    size_mb = f"{(size / (1024 * 1024)):.1f} MB" if size else "unknown"

    print(f"✅ Video Title: {title}")
    print(f"🎥 Duration: {duration_min}")
    print(f"🔈 Audio Language: {lang_code}")
    print(f"💾 Video Size (approx): {size_mb}")
    print(f"⬇️ Downloading video [{video_fmt}] and audio [{audio_fmt}]...")

    ydl_opts = {
        'outtmpl': os.path.join(download_dir, f"%(title)s.%(ext)s"),
        'format': f'{video_fmt}+{audio_fmt}',
        'merge_output_format': 'mp4',
        'writesubtitles': True,
        'subtitleslangs': [preferred_lang, 'en'],
        'quiet': False,
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    print(f"✅ Done! Saved to: {download_dir}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python youtube_bot.py <YouTube_URL> [language_code]")
        sys.exit(1)

    youtube_url = sys.argv[1]
    preferred_lang = sys.argv[2] if len(sys.argv) >= 3 else 'fr'
    download_video_audio(youtube_url, preferred_lang)
