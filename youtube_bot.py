import sys
import os
import re
import argparse
from yt_dlp import YoutubeDL

def sanitize_filename(name):
    return re.sub(r'[^a-zA-Z0-9_]+', '_', name)[:40].strip('_')

def download_youtube(url, lang='fr', mode='merged'):
    print(f"\n🎬 URL: {url}")
    print(f"🌍 Preferred Language: {lang}")
    print(f"🛠️ Mode: {mode}")

    base_dir = "Youtube_Bot_Downloads"
    os.makedirs(base_dir, exist_ok=True)

    # First, extract video info
    with YoutubeDL({'quiet': True, 'skip_download': True}) as ydl:
        info = ydl.extract_info(url, download=False)

    title = info.get('title', 'video')
    folder_name = sanitize_filename(title)
    download_dir = os.path.join(base_dir, folder_name)
    os.makedirs(download_dir, exist_ok=True)

    duration = info.get('duration', 0)
    formats = info.get('formats', [])
    duration_str = f"{duration // 60}m {duration % 60}s"
    subtitles = info.get('subtitles', {})

    best_video = None
    preferred_audio = None
    fallback_audio = None

    for f in formats:
        if f.get('vcodec') != 'none' and f.get('acodec') == 'none':
            if not best_video or f.get('height', 0) > best_video.get('height', 0):
                best_video = f
        elif f.get('acodec') != 'none' and f.get('vcodec') == 'none':
            lang_code = f.get('language') or ''
            if lang.lower() in lang_code.lower() and not preferred_audio:
                preferred_audio = f
            elif 'en' in lang_code.lower() and not fallback_audio:
                fallback_audio = f

    if not best_video or not (preferred_audio or fallback_audio):
        print("⚠️ Couldn't find split streams. Downloading best available merged stream.")
        ydl_opts = {
            'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
            'writesubtitles': True,
            'subtitleslangs': [lang, 'en'],
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return

    video_fmt = best_video['format_id']
    audio_fmt = (preferred_audio or fallback_audio)['format_id']
    audio_lang = (preferred_audio or fallback_audio).get('language', 'unknown')

    print(f"🎥 Title: {title}")
    print(f"⏱️ Duration: {duration_str}")
    print(f"🗣️ Audio Language: {audio_lang}")
    print(f"🎞️ Video Format: {video_fmt}, 🔊 Audio Format: {audio_fmt}")

    video_file = os.path.join(download_dir, f"x_video.{best_video['ext']}")
    audio_file = os.path.join(download_dir, f"x_audio.{audio_fmt}.{(preferred_audio or fallback_audio)['ext']}")
    sub_file   = os.path.join(download_dir, f"x_subtitles.{lang}.vtt")
    merged_file = os.path.join(download_dir, "x_merged.mp4")

    if mode in ['separate', 'both']:
        # Download separately
        ydl_opts_sep = {
            'outtmpl': os.path.join(download_dir, 'x_%(ext)s'),
            'format': f'{video_fmt}+{audio_fmt}',
            'merge_output_format': None,
            'postprocessors': [],
            'writesubtitles': True,
            'subtitleslangs': [lang, 'en'],
            'quiet': False,
        }
        with YoutubeDL(ydl_opts_sep) as ydl:
            ydl.download([url])
        os.rename(os.path.join(download_dir, 'x_webm'), audio_file)
        os.rename(os.path.join(download_dir, 'x_mp4'), video_file)

    if mode in ['merged', 'both']:
        ydl_opts_merge = {
            'outtmpl': merged_file,
            'format': f'{video_fmt}+{audio_fmt}',
            'merge_output_format': 'mp4',
            'writesubtitles': True,
            'subtitleslangs': [lang, 'en'],
            'quiet': False
        }
        with YoutubeDL(ydl_opts_merge) as ydl:
            ydl.download([url])

    print(f"✅ Download completed in: {download_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YouTube Multi-language Downloader Bot")
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("language", nargs='?', default="fr", help="Preferred audio/subtitle language (default: fr)")
    parser.add_argument("--mode", choices=['merged', 'separate', 'both'], default="merged", help="Download mode: merged, separate, or both")
    args = parser.parse_args()

    download_youtube(args.url, args.language, args.mode)
