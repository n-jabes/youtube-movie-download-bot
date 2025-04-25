import sys
import os
import re
from yt_dlp import YoutubeDL

DOWNLOAD_DIR = "Youtube_Bot_Downloads"

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', '', name).replace(' ', '_')[:100]

def download_video_audio(url, preferred_lang='fr'):
    print(f"\n🎬 Processing URL: {url}")
    print(f"🌍 Preferred audio language: {preferred_lang}")

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    ydl_opts_info = {'quiet': True, 'skip_download': True}
    with YoutubeDL(ydl_opts_info) as ydl:
        info = ydl.extract_info(url, download=False)

    title = sanitize_filename(info.get('title', 'video'))
    duration = info.get('duration', 0)
    duration_min = duration // 60
    formats = info.get('formats', [])

    best_video = None
    preferred_audio = None
    fallback_audio = None

    for f in formats:
        if f.get('vcodec') != 'none' and f.get('acodec') == 'none':
            if not best_video or f.get('height', 0) > best_video.get('height', 0):
                best_video = f
        elif f.get('acodec') != 'none' and f.get('vcodec') == 'none':
            lang = f.get('language') or ''
            if preferred_lang.lower() in lang.lower() and not preferred_audio:
                preferred_audio = f
            elif 'en' in lang.lower() and not fallback_audio:
                fallback_audio = f

    out_path = os.path.join(DOWNLOAD_DIR, f"{title}.mp4")

    if not best_video or not (preferred_audio or fallback_audio):
        print("⚠️ Couldn't find separate streams. Downloading best available with video+audio...")
        ydl_opts = {'outtmpl': out_path}
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"✅ Downloaded: {out_path}")
        print(f"⏱️ Duration: {duration_min} min")
        return

    video_fmt = best_video['format_id']
    audio_fmt = (preferred_audio or fallback_audio)['format_id']
    audio_lang = (preferred_audio or fallback_audio).get('language', 'unknown')
    total_size = ((best_video.get('filesize') or 0) + (preferred_audio or fallback_audio).get('filesize', 0)) / (1024**2)

    print(f"⬇️ Downloading video [{video_fmt}] and audio [{audio_fmt}]")
    print(f"📦 Estimated Size: {total_size:.2f} MB")
    print(f"🗣️ Audio Language: {audio_lang}")
    print(f"⏱️ Duration: {duration_min} min\n")

    ydl_opts = {
        'outtmpl': out_path,
        'format': f'{video_fmt}+{audio_fmt}',
        'merge_output_format': 'mp4',
        'quiet': False
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    print(f"\n✅ Download complete! Saved to: {out_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python youtube_bot.py <YouTube_URL> [language_code]")
        sys.exit(1)

    youtube_url = sys.argv[1]
    preferred_lang = sys.argv[2] if len(sys.argv) >= 3 else 'fr'
    download_video_audio(youtube_url, preferred_lang)
