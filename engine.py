import yt_dlp
import os
import shutil

# ──────────────────────────────────────────────
#  Silent logger (suppress yt-dlp console noise)
# ──────────────────────────────────────────────
class _SilentLogger:
    def debug(self, msg):   pass
    def warning(self, msg): pass
    def error(self, msg):   print(f"[ENGINE ERROR] {msg}")

# ──────────────────────────────────────────────
#  Shared yt-dlp headers & extractor args
# ──────────────────────────────────────────────
_COMMON_OPTS = {
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'source_address': '0.0.0.0',
    'simulate': True,
    'extractor_args': {
        'youtube': {
            'player_client': ['android', 'ios'],
            'player_skip': ['dash', 'hls']
        }
    },
    'http_headers': {
        'User-Agent': (
            'Mozilla/5.0 (Linux; Android 13; SM-S918B) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/120.0.0.0 Mobile Safari/537.36'
        )
    },
}

# ──────────────────────────────────────────────
#  Helper: extract & rank video formats
# ──────────────────────────────────────────────
def _extract_formats(info: dict) -> list[dict]:
    formats_dict: dict[str, dict] = {}
    for f in info.get('formats', []):
        vcodec    = f.get('vcodec', '')
        ext       = f.get('ext', '')
        height    = f.get('height')
        format_id = f.get('format_id')
        url       = f.get('url')

        if vcodec != 'none' and height and url:
            res = f"{height}p"
            score = 0
            if 'avc' in vcodec: score += 10
            if ext == 'mp4':    score += 5

            if res not in formats_dict or score > formats_dict[res]['score']:
                formats_dict[res] = {
                    'id':    format_id,
                    'res':   res,
                    'ext':   ext,
                    'url':   url,
                    'score': score,
                }

    sorted_formats = sorted(
        formats_dict.values(),
        key=lambda x: int(x['res'].replace('p', '')),
        reverse=True,
    )
    return [{'id': f['id'], 'res': f['res'], 'ext': f['ext'], 'url': f['url']} for f in sorted_formats]

def _get_best_video_with_audio(info: dict) -> str:
    best_video = None
    for f in info.get('formats', []):
        vcodec = f.get('vcodec', 'none')
        acodec = f.get('acodec', 'none')
        url = f.get('url')
        if vcodec != 'none' and acodec != 'none' and url:
            if not best_video or (f.get('height') or 0) > (best_video.get('height') or 0):
                best_video = f
    return best_video.get('url') if best_video else ''

def _get_best_audio(info: dict) -> str:
    best_audio = None
    for f in info.get('formats', []):
        vcodec = f.get('vcodec', 'none')
        acodec = f.get('acodec', 'none')
        url = f.get('url')
        if vcodec == 'none' and acodec != 'none' and url:
            if not best_audio or (f.get('abr') or 0) > (best_audio.get('abr') or 0):
                best_audio = f
    return best_audio.get('url') if best_audio else ''

# ──────────────────────────────────────────────
#  Public API functions
# ──────────────────────────────────────────────
def check_ffmpeg() -> bool:
    """Return True if ffmpeg is available on this machine."""
    return shutil.which('ffmpeg') is not None or os.path.exists('ffmpeg.exe')

def get_info(url: str) -> dict:
    """Fetch metadata for a single video, search query, or a playlist."""
    is_search = url.startswith('ytsearch')
    opts = {
        **_COMMON_OPTS,
        'logger': _SilentLogger(),
    }
    
    if not is_search:
        opts['extract_flat'] = 'in_playlist'

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)

            if 'entries' in info:
                entries = list(info['entries'])
                if is_search and len(entries) > 0:
                    video_info = entries[0]
                    return {
                        'type':     'video',
                        'title':    video_info.get('title'),
                        'thumb':    video_info.get('thumbnail'),
                        'duration': video_info.get('duration'),
                        'uploader': video_info.get('uploader'),
                        'best_video': _get_best_video_with_audio(video_info),
                        'best_audio': _get_best_audio(video_info),
                        'formats':  _extract_formats(video_info),
                    }
                else:
                    videos = [
                        {'title': e.get('title'), 'url': e.get('url')}
                        for e in entries if e.get('url')
                    ]
                    return {
                        'type':   'playlist',
                        'title':  info.get('title'),
                        'count':  len(videos),
                        'videos': videos,
                    }
            else:
                return {
                    'type':     'video',
                    'title':    info.get('title'),
                    'thumb':    info.get('thumbnail'),
                    'duration': info.get('duration'),
                    'uploader': info.get('uploader'),
                    'best_video': _get_best_video_with_audio(info),
                    'best_audio': _get_best_audio(info),
                    'formats':  _extract_formats(info),
                }
    except Exception as exc:
        return {'type': 'error', 'message': str(exc)}
