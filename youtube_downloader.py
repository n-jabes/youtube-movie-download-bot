import os
import re
import sys
import time
import argparse
from yt_dlp import YoutubeDL, DownloadError
import requests
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from difflib import SequenceMatcher

# Constants
TMDB_API_KEY = "your_tmdb_api_key" # Replace with your/company's TMDB API Read Access Token
TMDB_BASE_URL = 'https://api.themoviedb.org/3'
YOUTUBE_SEARCH_TEMPLATE = "{} {} full movie"  # Template for YouTube search query
MAX_DURATION_DIFF = 3 * 60  # Maximum duration difference in seconds (+/- 3 minutes)

def spinner():
    """Show a simple spinner animation for loading states"""
    chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    while True:
        for char in chars:
            yield char

def print_loading(message):
    """Display a loading message with spinner"""
    spin = spinner()
    sys.stdout.write(f"\r{next(spin)} {message}...")
    sys.stdout.flush()

def sanitize_filename(name):
    """Create a safe filename from the video title"""
    return re.sub(r'[^a-zA-Z0-9_]+', '_', name).strip('_')[:40]

def print_formats(formats):
    """Display available formats in a readable way"""
    print("\n📋 Available Formats:")
    for f in formats:
        lang = f.get('language') or '-'
        resolution = f"{f.get('height', '-')}p" if f.get('height') else '-'
        print(f"  ID: {f.get('format_id'):<7} | ext: {f.get('ext', '-'):<5} | lang: {lang:<5} | res: {resolution:<6} | note: {f.get('format_note', '-'):<15}")

def get_tmdb_movie_details(movie_id):
    """Fetch movie details from TMDB API"""
    headers = {
        'Authorization': f'Bearer {TMDB_API_KEY}',
        'Content-Type': 'application/json;charset=utf-8'
    }
    
    try:
        url = f"{TMDB_BASE_URL}/movie/{movie_id}"
        print_loading("Fetching movie details from TMDB")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        movie_data = response.json()
        
        videos_url = f"{TMDB_BASE_URL}/movie/{movie_id}/videos"
        response = requests.get(videos_url, headers=headers)
        response.raise_for_status()
        videos_data = response.json()
        
        credits_url = f"{TMDB_BASE_URL}/movie/{movie_id}/credits"
        response = requests.get(credits_url, headers=headers)
        response.raise_for_status()
        credits_data = response.json()
        
        release_url = f"{TMDB_BASE_URL}/movie/{movie_id}/release_dates"
        response = requests.get(release_url, headers=headers)
        response.raise_for_status()
        release_data = response.json()
        
        directors = [crew['name'] for crew in credits_data.get('crew', []) if crew['job'] == 'Director']
        main_actors = [cast['name'] for cast in credits_data.get('cast', [])][:3]
        
        certification = None
        for country in release_data.get('results', []):
            if country['iso_3166_1'] == 'US':
                for release in country.get('release_dates', []):
                    if release.get('certification'):
                        certification = release['certification']
                        break
        
        youtube_videos = [v for v in videos_data.get('results', []) if v['site'] == 'YouTube']
        
        result = {
            'title': movie_data.get('title'),
            'original_title': movie_data.get('original_title'),
            'year': movie_data.get('release_date', '')[:4] if movie_data.get('release_date') else 'Unknown',
            'directors': directors,
            'main_actors': main_actors,
            'runtime': movie_data.get('runtime'),
            'genres': [g['name'] for g in movie_data.get('genres', [])],
            'certification': certification,
            'youtube_videos': youtube_videos,
            'overview': movie_data.get('overview'),
            'poster_path': f"https://image.tmdb.org/t/p/original{movie_data.get('poster_path', '')}" if movie_data.get('poster_path') else None,
            'backdrop_path': f"https://image.tmdb.org/t/p/original{movie_data.get('backdrop_path', '')}" if movie_data.get('backdrop_path') else None,
            'status': 'success'
        }
        
        print(f"\r✅ Fetched movie details from TMDB successfully")
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"\r❌ Failed to fetch TMDB data: {str(e)}")
        return {'status': 'error', 'message': str(e)}

def display_movie_info(movie_data):
    """Display the movie information in a user-friendly way"""
    print("\n🎬 Movie Information:")
    print(f"  Title: {movie_data.get('title')} ({movie_data.get('original_title')})")
    print(f"  Year: {movie_data.get('year')}")
    print(f"  Runtime: {movie_data.get('runtime', 'Unknown')} minutes")
    print(f"  Certification: {movie_data.get('certification', 'Not rated')}")
    print(f"  Genres: {', '.join(movie_data.get('genres', []))}")
    print(f"  Directors: {', '.join(movie_data.get('directors', []))}")
    print(f"  Main Actors: {', '.join(movie_data.get('main_actors', []))}")
    print(f"\n📝 Overview: {movie_data.get('overview', 'No overview available')}")
    
    if movie_data.get('youtube_videos'):
        print(f"\n🎥 Found {len(movie_data['youtube_videos'])} YouTube video(s) from TMDB:")
        for i, video in enumerate(movie_data['youtube_videos'], 1):
            print(f"  {i}. {video['name']} (Type: {video['type']}) - https://www.youtube.com/watch?v={video['key']}")

def calculate_match_score(video_info, movie_data):
    """
    Calculate a match score between YouTube video and TMDB movie based on:
    1. Title similarity (40% weight)
    2. Duration match (30% weight)
    3. Presence of "full movie" in title (10% weight)
    4. Year match (10% weight)
    5. TMDB official video (10% weight if applicable)
    """
    score = 0
    video_title = video_info.get('title', '').lower()
    movie_title = movie_data.get('title', '').lower()
    original_title = movie_data.get('original_title', '').lower()
    movie_year = movie_data.get('year', '')
    
    # 1. Title similarity (40%)
    title_similarity = max(
        SequenceMatcher(None, video_title, movie_title).ratio(),
        SequenceMatcher(None, video_title, original_title).ratio()
    )
    score += title_similarity * 0.4
    
    # 2. Duration match (30%)
    if movie_data.get('runtime') and video_info.get('duration'):
        tmdb_duration = movie_data['runtime'] * 60  # Convert to seconds
        duration_diff = abs(video_info['duration'] - tmdb_duration)
        if duration_diff <= MAX_DURATION_DIFF:
            duration_score = 1 - (duration_diff / MAX_DURATION_DIFF)
            score += duration_score * 0.3
    
    # 3. "Full movie" in title (10%)
    if 'full movie' in video_title or 'full film' in video_title:
        score += 0.1
    
    # 4. Year match (10%)
    if movie_year and movie_year in video_title:
        score += 0.1
    
    # 5. TMDB official video (10%)
    if video_info.get('is_tmdb_official', False):
        score += 0.1
    
    return min(score, 1.0)  # Cap at 1.0

def search_youtube_full_movie(movie_data, lang='fr'):
    """Search YouTube for the best matching full movie based on TMDB data"""
    print("\n🔍 Searching YouTube for best matching movie...")
    
    # First check TMDB official videos
    if movie_data.get('youtube_videos'):
        for video in movie_data['youtube_videos']:
            if video['type'].lower() in ('full movie', 'movie'):
                print(f"✅ Using official full movie from TMDB data: {video['name']}")
                return f"https://www.youtube.com/watch?v={video['key']}"
    
    # Construct search query
    query = YOUTUBE_SEARCH_TEMPLATE.format(
        movie_data.get('title'),
        movie_data.get('year'),
        " ".join(movie_data.get('genres', [])[:1])
    )
    
    print(f"  Searching YouTube for: '{query}'")
    
    try:
        with YoutubeDL({
            'quiet': True,
            'extract_flat': False,
            'default_search': 'ytsearch20',
            'socket_timeout': 30,
            'extractor_retries': 3,
            'force_generic_extractor': True  # Added to help with URL extraction
        }) as ydl:
            result = ydl.extract_info(query, download=False)
            
            if not result or 'entries' not in result or not result['entries']:
                print("⚠️ No YouTube videos found matching the query")
                return None
                
            # Score all videos and find the best match
            best_match = None
            best_score = 0
            
            for video in result['entries']:
                try:
                    current_score = calculate_match_score(video, movie_data)
                    if current_score > best_score:
                        best_score = current_score
                        best_match = video
                except Exception as e:
                    continue
            
            if best_match:
                print(f"\n🏆 Best Match Found:")
                print(f"  Title: {best_match.get('title')}")
                
                # Get the URL - trying multiple methods
                url = best_match.get('url') or best_match.get('webpage_url')
                if not url and best_match.get('id'):
                    url = f"https://www.youtube.com/watch?v={best_match['id']}"
                
                if url:
                    print(f"  URL: {url}")
                    print(f"  Duration: {best_match.get('duration', 0)//60}m {best_match.get('duration', 0)%60}s")
                    print(f"  Match Score: {best_score:.2f}/1.00")
                    
                    if best_score < 0.5:
                        print("⚠️ Warning: Match quality is low, but will attempt download anyway")
                    
                    return url
                else:
                    print("⚠️ Could not extract URL for best match")
                    return None
            else:
                print("⚠️ No suitable matches found, trying first result")
                first_video = result['entries'][0]
                url = first_video.get('url') or first_video.get('webpage_url')
                if not url and first_video.get('id'):
                    url = f"https://www.youtube.com/watch?v={first_video['id']}"
                return url if url else None
                
    except Exception as e:
        print(f"⚠️ YouTube search failed, trying fallback method: {str(e)}")
        # Fallback to simple search
        try:
            with YoutubeDL({
                'quiet': True,
                'extract_flat': True,
                'default_search': 'ytsearch1',
                'force_generic_extractor': True
            }) as ydl:
                result = ydl.extract_info(query, download=False)
                if result and 'entries' in result and result['entries']:
                    video = result['entries'][0]
                    url = video.get('url') or video.get('webpage_url')
                    if not url and video.get('id'):
                        url = f"https://www.youtube.com/watch?v={video['id']}"
                    return url if url else None
        except Exception as e:
            print(f"⚠️ Fallback search also failed: {str(e)}")
        
        print("❌ Could not find any YouTube video")
        return None

def check_language_availability(url, lang='fr'):
    """Check if audio or subtitles are available in the specified language"""
    print(f"\n🔍 Checking language availability for {url}")
    print(f"🌍 Preferred Language: {lang}")
    
    try:
        with YoutubeDL({'quiet': True, 'skip_download': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            
        formats = info.get('formats', [])
        subtitles = info.get('subtitles', {})
        
        has_preferred_audio = any(
            f.get('acodec') != 'none' and lang.lower() in (f.get('language') or '').lower() 
            for f in formats
        )
        
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
    if not url:
        print("❌ No valid URL provided for download")
        return False
        
    print(f"\n🎬 URL: {url}")
    print(f"🌍 Preferred Language: {lang}")
    print(f"🛠️ Mode: {mode}")
    
    if mode == 'check':
        return check_language_availability(url, lang)
    
    base_dir = "Youtube_Bot_Downloads"
    os.makedirs(base_dir, exist_ok=True)
    
    try:
        with YoutubeDL({'quiet': not verbose, 'skip_download': True}) as ydl:
            info = ydl.extract_info(url, download=False)
    except DownloadError as e:
        print(f"❌ Error extracting video info: {e}")
        return False
    
    title = info.get('title', 'video')
    clean_name = sanitize_filename(title)
    download_dir = os.path.join(base_dir, clean_name)
    os.makedirs(download_dir, exist_ok=True)
    
    duration = info.get('duration', 0)
    formats = info.get('formats', [])
    duration_str = f"{duration // 60}m {duration % 60}s"
    
    print(f"🎥 Title: {title}")
    print(f"⏱️ Duration: {duration_str}")
    
    if verbose:
        print_formats(formats)
    
    best_video = None
    preferred_audio = None
    fallback_audio = None
    
    for f in formats:
        if f.get('vcodec') != 'none' and f.get('acodec') == 'none' and f.get('protocol') != 'm3u8_native':
            if not best_video or f.get('height', 0) > best_video.get('height', 0):
                best_video = f
        
        elif f.get('acodec') != 'none' and f.get('vcodec') == 'none' and f.get('protocol') != 'm3u8_native':
            language = f.get('language') or ''
            if lang.lower() in language.lower() and (not preferred_audio or f.get('tbr', 0) > preferred_audio.get('tbr', 0)):
                preferred_audio = f
            elif 'en' in language.lower() and (not fallback_audio or f.get('tbr', 0) > fallback_audio.get('tbr', 0)):
                fallback_audio = f
    
    if not preferred_audio and not fallback_audio:
        for f in formats:
            if f.get('acodec') != 'none' and f.get('vcodec') == 'none' and f.get('protocol') != 'm3u8_native':
                if not fallback_audio or f.get('tbr', 0) > fallback_audio.get('tbr', 0):
                    fallback_audio = f
    
    audio_stream = preferred_audio or fallback_audio
    
    video_fmt = best_video['format_id'] if best_video else 'bestvideo'
    audio_fmt = audio_stream['format_id'] if audio_stream else 'bestaudio'
    video_ext = best_video['ext'] if best_video else 'mp4'
    audio_ext = audio_stream['ext'] if audio_stream else 'm4a'
    audio_lang = audio_stream.get('language', 'unknown') if audio_stream else 'unknown'
    
    base_file = os.path.join(download_dir, clean_name)
    merged_file = f"{base_file}_merged.mp4"
    video_file = f"{base_file}_video.{video_ext}"
    audio_file = f"{base_file}_audio_{audio_lang}.{audio_ext}"
    
    print(f"\n📊 Stream Selection:")
    print(f"  • Video: {video_fmt} ({best_video['height']}p)" if best_video else "  • Video: best available")
    print(f"  • Audio: {audio_fmt} (Language: {audio_lang})" if audio_stream else "  • Audio: best available")
    
    download_success = False
    
    def run_download(opts):
        try:
            with YoutubeDL(opts) as ydl:
                ydl.download([url])
            return True
        except DownloadError as e:
            print(f"❌ Download failed: {e}")
            return False
    
    if mode in ['separate', 'both']:
        print("\n🔽 Downloading separate video and audio streams...")
        
        video_opts = {
            'outtmpl': video_file,
            'format': f'{video_fmt}/bestvideo',
            'quiet': not verbose,
            'progress': verbose,
            'postprocessors': [],
            'writesubtitles': False,
            'socket_timeout': 120,
            'retries': 10,
            'fragment_retries': 10,
            'extractor_retries': 5
        }
        
        video_success = run_download(video_opts)
        if video_success:
            print(f"✅ Video stream saved: {os.path.basename(video_file)}")
        
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

def process_movie(movie_id, lang='fr', mode='merged', verbose=False):
    """Main function to process a movie from TMDB ID to YouTube download"""
    try:
        movie_data = get_tmdb_movie_details(movie_id)
        if movie_data.get('status') == 'error':
            print(f"❌ Failed to process movie: {movie_data.get('message')}")
            return False
        
        display_movie_info(movie_data)
        
        youtube_url = search_youtube_full_movie(movie_data, lang)
        if not youtube_url:
            print("❌ No suitable video found for download")
            return False
        
        return download_youtube(youtube_url, lang, mode, verbose)
        
    except Exception as e:
        print(f"❌ Unexpected error processing movie: {str(e)}")
        if verbose:
            import traceback
            traceback.print_exc()
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TMDB to YouTube Downloader Bot")
    parser.add_argument("movie_id", help="TMDB movie ID")
    parser.add_argument("--lang", default="fr", help="Preferred audio/subtitle language (default: fr)")
    parser.add_argument("--mode", choices=['merged', 'separate', 'both', 'check'], default="merged", 
                        help="Download mode: merged (video+audio together), separate (video and audio as separate files), both (try both methods), or check (just check language availability without downloading)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show verbose output")
    
    args = parser.parse_args()
    
    if not TMDB_API_KEY or TMDB_API_KEY == 'your_tmdb_api_key':
        print("❌ Error: You need to set your TMDB API key in the script")
        sys.exit(1)
    
    success = process_movie(args.movie_id, args.lang, args.mode, args.verbose)
    sys.exit(0 if success else 1)