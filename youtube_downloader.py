import os
import re
import sys
import argparse
from yt_dlp import YoutubeDL, DownloadError

def sanitize_filename(name):
    """Create a safe filename from the video title"""
    return re.sub(r'[^a-zA-Z0-9_]+', '_', name).strip('_')[:40]

def print_formats(formats):
    """Display available formats in a readable way"""
    print("📋 Available Formats:")
    for f in formats:
        lang = f.get('language') or '-'
        resolution = f"{f.get('height', '-')}p" if f.get('height') else '-'
        print(f"  ID: {f.get('format_id'):<7} | ext: {f.get('ext', '-'):<5} | lang: {lang:<5} | res: {resolution:<6} | note: {f.get('format_note', '-'):<15}")

def check_language_availability(url, lang='fr'):
    """Check if audio or subtitles are available in the specified language"""
    print(f"\n🔍 Checking language availability for {url}")
    print(f"🌍 Preferred Language: {lang}")
    
    try:
        with YoutubeDL({'quiet': True, 'skip_download': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            
        formats = info.get('formats', [])
        subtitles = info.get('subtitles', {})
        
        # Check for audio in preferred language
        has_preferred_audio = any(
            f.get('acodec') != 'none' and lang.lower() in (f.get('language') or '').lower() 
            for f in formats
        )
        
        # Check for subtitles in preferred language
        has_preferred_subs = lang in subtitles
        
        print(f"✅ Audio in {lang}: {has_preferred_audio}")
        print(f"✅ Subtitles in {lang}: {has_preferred_subs}")
        
        return {
            "audio_available": has_preferred_audio,
            "subtitles_available": has_preferred_subs,
            "title": info.get('title', 'Unknown')
        }
        
    except DownloadError as e:
        print(f"❌ Error checking language availability: {e}")
        return {
            "audio_available": False,
            "subtitles_available": False,
            "error": str(e)
        }

def download_youtube(url, lang='fr', mode='merged', verbose=False):
    """Download YouTube video according to specified parameters"""
    print(f"\n🎬 URL: {url}")
    print(f"🌍 Preferred Language: {lang}")
    print(f"🛠️ Mode: {mode}")
    
    # Check mode - just return language availability without downloading
    if mode == 'check':
        return check_language_availability(url, lang)
    
    # Create output directory structure
    base_dir = "Youtube_Bot_Downloads"
    os.makedirs(base_dir, exist_ok=True)
    
    # Get video information without downloading
    try:
        with YoutubeDL({'quiet': not verbose, 'skip_download': True}) as ydl:
            info = ydl.extract_info(url, download=False)
    except DownloadError as e:
        print(f"❌ Error extracting video info: {e}")
        return False
    
    # Prepare filenames and directories
    title = info.get('title', 'video')
    clean_name = sanitize_filename(title)
    download_dir = os.path.join(base_dir, clean_name)
    os.makedirs(download_dir, exist_ok=True)
    
    # Display video information
    duration = info.get('duration', 0)
    formats = info.get('formats', [])
    duration_str = f"{duration // 60}m {duration % 60}s"
    
    print(f"🎥 Title: {title}")
    print(f"⏱️ Duration: {duration_str}")
    
    if verbose:
        print_formats(formats)
    
    # Find best video and audio streams
    best_video = None
    preferred_audio = None
    fallback_audio = None
    
    for f in formats:
        # Look for video-only streams of highest quality
        if f.get('vcodec') != 'none' and f.get('acodec') == 'none' and f.get('protocol') != 'm3u8_native':
            if not best_video or f.get('height', 0) > best_video.get('height', 0):
                best_video = f
        
        # Look for audio-only streams with preferred language or English fallback
        elif f.get('acodec') != 'none' and f.get('vcodec') == 'none' and f.get('protocol') != 'm3u8_native':
            language = f.get('language') or ''
            if lang.lower() in language.lower() and (not preferred_audio or f.get('tbr', 0) > preferred_audio.get('tbr', 0)):
                preferred_audio = f
            elif 'en' in language.lower() and (not fallback_audio or f.get('tbr', 0) > fallback_audio.get('tbr', 0)):
                fallback_audio = f
    
    # If we can't find language-specific audio, use best audio
    if not preferred_audio and not fallback_audio:
        for f in formats:
            if f.get('acodec') != 'none' and f.get('vcodec') == 'none' and f.get('protocol') != 'm3u8_native':
                if not fallback_audio or f.get('tbr', 0) > fallback_audio.get('tbr', 0):
                    fallback_audio = f
    
    # Choose the best available audio stream
    audio_stream = preferred_audio or fallback_audio
    
    # Determine format IDs and file extensions
    video_fmt = best_video['format_id'] if best_video else 'bestvideo'
    audio_fmt = audio_stream['format_id'] if audio_stream else 'bestaudio'
    video_ext = best_video['ext'] if best_video else 'mp4'
    audio_ext = audio_stream['ext'] if audio_stream else 'm4a'
    audio_lang = audio_stream.get('language', 'unknown') if audio_stream else 'unknown'
    
    # Prepare output filenames
    base_file = os.path.join(download_dir, clean_name)
    merged_file = f"{base_file}_merged.mp4"
    video_file = f"{base_file}_video.{video_ext}"
    audio_file = f"{base_file}_audio_{audio_lang}.{audio_ext}"
    
    print(f"\n📊 Stream Selection:")
    print(f"  • Video: {video_fmt} ({best_video['height']}p)" if best_video else "  • Video: best available")
    print(f"  • Audio: {audio_fmt} (Language: {audio_lang})" if audio_stream else "  • Audio: best available")
    
    download_success = False
    
    # Function to execute downloads with given options
    def run_download(opts):
        try:
            with YoutubeDL(opts) as ydl:
                ydl.download([url])
            return True
        except DownloadError as e:
            print(f"❌ Download failed: {e}")
            return False
    
    # Download separate streams if requested
    if mode in ['separate', 'both']:
        print("\n🔽 Downloading separate video and audio streams...")
        
        # Download video stream
        video_opts = {
    'outtmpl': video_file,
    'format': f'{video_fmt}/bestvideo',
    'quiet': not verbose,
    'progress': verbose,
    'postprocessors': [],
    'writesubtitles': False,
    'socket_timeout': 120,  # Increase socket timeout to 120 seconds
    'retries': 10,         # Retry up to 10 times
    'fragment_retries': 10, # Retry fragments up to 10 times
    'extractor_retries': 5  # Retry extraction up to 5 times
}
        
        video_success = run_download(video_opts)
        if video_success:
            print(f"✅ Video stream saved: {os.path.basename(video_file)}")
        
        # Download audio stream
        audio_opts = {
            'outtmpl': audio_file,
            'format': f'{audio_fmt}/bestaudio',
            'quiet': not verbose,
            'progress': verbose,
            'postprocessors': [],
            'writesubtitles': False
        }
        
        audio_success = run_download(audio_opts)
        if audio_success:
            print(f"✅ Audio stream saved: {os.path.basename(audio_file)}")
        
        # Download subtitles
        subtitle_opts = {
            'outtmpl': f"{base_file}",
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': [lang, 'en'],
            'quiet': not verbose,
            'progress': verbose
        }
        
        subtitle_success = run_download(subtitle_opts)
        if subtitle_success:
            print(f"✅ Subtitles downloaded (if available)")
        
        download_success = video_success or audio_success
    
    # Download merged file if requested or if separate download failed
    if mode == 'merged' or (mode == 'both' and not download_success):
        if mode == 'both' and not download_success:
            print("\n🔁 Fallback: Downloading merged file since separate streams failed...")
        else:
            print("\n🔽 Downloading merged video+audio file...")
        
        merge_opts = {
            'outtmpl': merged_file,
            'format': f'{video_fmt}+{audio_fmt}/best',
            'merge_output_format': 'mp4',
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': [lang, 'en'],
            'quiet': not verbose,
            'progress': verbose
        }
        
        merged_success = run_download(merge_opts)
        
        if merged_success:
            print(f"✅ Merged video+audio saved: {os.path.basename(merged_file)}")
            download_success = True
    
    if download_success:
        print(f"\n📁 All output saved to: {download_dir}")
        return True
    else:
        print("\n❌ Download failed completely.")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YouTube Downloader Bot")
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("--lang", default="fr", help="Preferred audio/subtitle language (default: fr)")
    parser.add_argument("--mode", choices=['merged', 'separate', 'both', 'check'], default="merged", 
                        help="Download mode: merged (video+audio together), separate (video and audio as separate files), both (try both methods), or check (just check language availability without downloading)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show verbose output")
    
    args = parser.parse_args()
    
    download_youtube(args.url, args.lang, args.mode, args.verbose)