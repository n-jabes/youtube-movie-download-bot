
import sys
import os
import re
import argparse
from yt_dlp import YoutubeDL, DownloadError

def sanitize_filename(name):
    return re.sub(r'[^a-zA-Z0-9_]+', '_', name)[:40].strip('_')

def download_youtube(url, lang='fr', mode='merged'):
    print(f"\\n🎬 URL: {url}")
    print(f"🌍 Preferred Language: {lang}")
    print(f"🛠️ Mode: {mode}")

    base_dir = "Youtube_Bot_Downloads"
    os.makedirs(base_dir, exist_ok=True)

    with YoutubeDL({'quiet': True, 'skip_download': True}) as ydl:
        info = ydl.extract_info(url, download=False)

    title = info.get('title', 'video')
    clean_name = sanitize_filename(title)
    download_dir = os.path.join(base_dir, clean_name)
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
    video_ext = best_video['ext']
    audio_ext = (preferred_audio or fallback_audio)['ext']

    print(f"🎥 Title: {title}")
    print(f"⏱️ Duration: {duration_str}")
    print(f"🗣️ Audio Language: {audio_lang}")
    print(f"🎞️ Video Format: {video_fmt}, 🔊 Audio Format: {audio_fmt}")

    merged_file = os.path.join(download_dir, f"{clean_name}_merged.mp4")
    video_file = os.path.join(download_dir, f"{clean_name}_video.{video_ext}")
    audio_file = os.path.join(download_dir, f"{clean_name}_audio.{audio_ext}")
    subtitle_file = os.path.join(download_dir, f"{clean_name}_subtitles.{lang}.vtt")

    if mode in ['separate', 'both']:
        sep_opts = {
            'outtmpl': os.path.join(download_dir, f"{clean_name}_%(id)s.%(ext)s"),
            'format': f"{video_fmt}+{audio_fmt}",
            'merge_output_format': None,
            'postprocessors': [],
            'writesubtitles': True,
            'subtitleslangs': [lang, 'en'],
            'quiet': False
        }
        try:
            with YoutubeDL(sep_opts) as ydl:
                ydl.download([url])

            vid_temp = os.path.join(download_dir, f"{clean_name}_{video_fmt}.{video_ext}")
            aud_temp = os.path.join(download_dir, f"{clean_name}_{audio_fmt}.{audio_ext}")
            if os.path.exists(vid_temp):
                os.rename(vid_temp, video_file)
            if os.path.exists(aud_temp):
                os.rename(aud_temp, audio_file)
        except DownloadError:
            print("⚠️ Separate download failed. Falling back to merged mode.")
            mode = 'merged'

    if mode in ['merged', 'both']:
        merge_opts = {
            'outtmpl': merged_file,
            'format': f'{video_fmt}+{audio_fmt}',
            'merge_output_format': 'mp4',
            'writesubtitles': True,
            'subtitleslangs': [lang, 'en'],
            'quiet': False
        }
        with YoutubeDL(merge_opts) as ydl:
            ydl.download([url])

    print(f"✅ Download complete! Files saved in: {download_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YouTube Multi-language Downloader Bot")
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("language", nargs='?', default="fr", help="Preferred audio/subtitle language (default: fr)")
    parser.add_argument("--mode", choices=['merged', 'separate', 'both'], default="merged", help="Download mode: merged, separate, or both")
    args = parser.parse_args()

    download_youtube(args.url, args.language, args.mode)
