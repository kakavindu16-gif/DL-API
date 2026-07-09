"""
Syntiox DL-API — /info Endpoint Test
=====================================
Run from DL-API root:
    python test/test.py [URL]

Output files (saved in test/ folder):
    test1.txt — Complete metadata
    test2.txt — All formats with FULL URLs
"""

import sys
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone

# ── Config ────────────────────────────────────────────────────────────────────
BASE_URL  = "http://localhost:8000"
API_KEY   = "dev-api-key"
TEST_URL  = sys.argv[1] if len(sys.argv) > 1 else "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── ANSI Colors ───────────────────────────────────────────────────────────────
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    CYAN    = "\033[96m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    RED     = "\033[91m"
    MAGENTA = "\033[95m"
    BLUE    = "\033[94m"
    WHITE   = "\033[97m"

def hr(char="─", length=70, color=C.DIM):
    print(f"{color}{char * length}{C.RESET}")

def section(title: str, color=C.CYAN):
    print()
    hr("═", color=color)
    print(f"{color}{C.BOLD}  {title}{C.RESET}")
    hr("═", color=color)

def field(label: str, value, color=C.WHITE, unit=""):
    if value is None or value == "" or value == []:
        value_str = f"{C.DIM}(නැත){C.RESET}"
    elif isinstance(value, bool):
        value_str = f"{C.GREEN}✔ ඔව්{C.RESET}" if value else f"{C.DIM}✘ නැත{C.RESET}"
    elif isinstance(value, (int, float)):
        value_str = f"{C.YELLOW}{value:,}{C.RESET}{C.DIM} {unit}{C.RESET}" if unit else f"{C.YELLOW}{value:,}{C.RESET}"
    else:
        value_str = f"{color}{value}{C.RESET}"
    print(f"  {C.DIM}{label:<22}{C.RESET} {value_str}")

def fmt_date(d: str) -> str:
    if not d or len(d) != 8:
        return str(d) if d else "(නැත)"
    try:
        return datetime.strptime(d, "%Y%m%d").strftime("%Y %b %d")
    except Exception:
        return d

def fmt_size(b) -> str:
    if not b:
        return "(නැත)"
    b = int(b)
    for unit in ["B", "KB", "MB", "GB"]:
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} TB"

def fmt_ts(ts) -> str:
    if not ts:
        return "(නැත)"
    try:
        return datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        return str(ts)

def shorten_url(url: str, max_len=65) -> str:
    if not url:
        return "(නැත)"
    return url[:max_len] + "..." if len(url) > max_len else url

# ── File save helpers ─────────────────────────────────────────────────────────
def v(val, unit="") -> str:
    """Format a value for plain text output."""
    if val is None or val == "":
        return "(නැත)"
    if isinstance(val, bool):
        return "ඔව්" if val else "නැත"
    if isinstance(val, (int, float)) and unit:
        return f"{val:,} {unit}"
    if isinstance(val, (int, float)):
        return f"{val:,}"
    return str(val)

def save_test1(data: dict):
    """Save complete metadata to test1.txt"""
    path = os.path.join(SCRIPT_DIR, "test1.txt")
    lines = []
    sep = "=" * 80

    lines.append(sep)
    lines.append("  Syntiox DL-API — /info Response — test1.txt (Metadata)")
    lines.append(f"  Generated : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"  URL       : {TEST_URL}")
    lines.append(sep)

    # Basic info
    lines.append("\n[ මූලික තොරතුරු ]" + "-"*60)
    lines.append(f"  {'Title':<22} {v(data.get('title'))}")
    lines.append(f"  {'Platform':<22} {v(data.get('extractor'))}")
    lines.append(f"  {'Type':<22} {v(data.get('type'))}")
    lines.append(f"  {'Duration':<22} {v(data.get('duration_string'))} ({v(data.get('duration'))}s)")
    lines.append(f"  {'Uploader':<22} {v(data.get('uploader'))}")
    lines.append(f"  {'Uploader ID':<22} {v(data.get('uploader_id'))}")
    lines.append(f"  {'Channel':<22} {v(data.get('channel'))}")
    lines.append(f"  {'Channel ID':<22} {v(data.get('channel_id'))}")
    lines.append(f"  {'Channel URL':<22} {v(data.get('channel_url'))}")
    lines.append(f"  {'Webpage URL':<22} {v(data.get('webpage_url'))}")
    lines.append(f"  {'Language':<22} {v(data.get('language'))}")
    lines.append(f"  {'Age Limit':<22} {v(data.get('age_limit'))}+")
    lines.append(f"  {'Is Live':<22} {v(data.get('is_live'))}")
    lines.append(f"  {'Was Live':<22} {v(data.get('was_live'))}")
    lines.append(f"  {'Thumbnail':<22} {v(data.get('thumb'))}")

    # Stats
    lines.append("\n[ ස්ටැට්ස් ]" + "-"*60)
    lines.append(f"  {'Views':<22} {v(data.get('view_count'), 'views')}")
    lines.append(f"  {'Likes':<22} {v(data.get('like_count'), 'likes')}")
    lines.append(f"  {'Dislikes':<22} {v(data.get('dislike_count'), 'dislikes')}")
    lines.append(f"  {'Comments':<22} {v(data.get('comment_count'), 'comments')}")
    lines.append(f"  {'Average Rating':<22} {v(data.get('average_rating'))}")
    lines.append(f"  {'Upload Date':<22} {fmt_date(data.get('upload_date',''))}")
    lines.append(f"  {'Timestamp':<22} {fmt_ts(data.get('timestamp'))}")

    # Tags & Categories
    lines.append("\n[ Tags & Categories ]" + "-"*60)
    cats = data.get("categories") or []
    tags = data.get("tags") or []
    lines.append(f"  {'Categories':<22} {', '.join(cats) if cats else '(නැත)'}")
    if tags:
        lines.append(f"  Tags ({len(tags)} total):")
        for i in range(0, len(tags), 5):
            lines.append("    " + ", ".join(tags[i:i+5]))
    else:
        lines.append(f"  {'Tags':<22} (නැත)")

    # Description
    lines.append("\n[ Description ]" + "-"*60)
    desc = data.get("description") or ""
    if desc:
        for line in desc.strip().splitlines():
            lines.append(f"  {line}")
    else:
        lines.append("  (නැත)")

    # Best Video
    lines.append("\n[ Best Video Stream ]" + "-"*60)
    meta = data.get("best_video_meta") or {}
    lines.append(f"  {'Resolution':<22} {meta.get('width')}x{meta.get('height')} @ {meta.get('fps','')}fps")
    lines.append(f"  {'Video Codec':<22} {v(meta.get('vcodec'))}")
    lines.append(f"  {'Audio Codec':<22} {v(meta.get('acodec'))}")
    lines.append(f"  {'Extension':<22} {v(meta.get('ext'))}")
    lines.append(f"  {'File Size':<22} {fmt_size(meta.get('filesize'))}")
    lines.append(f"\n  Stream URL (JWT):")
    lines.append(f"  {data.get('best_video_download_url','(නැත)')}")
    lines.append(f"\n  Direct URL (Raw CDN):")
    lines.append(f"  {data.get('best_video_direct_url','(නැත)')}")

    # Best Audio
    lines.append("\n[ Best Audio Stream ]" + "-"*60)
    ameta = data.get("audio_meta") or {}
    lines.append(f"  {'Bitrate':<22} {v(ameta.get('abr'), 'kbps')}")
    lines.append(f"  {'Audio Codec':<22} {v(ameta.get('acodec'))}")
    lines.append(f"  {'Extension':<22} {v(ameta.get('ext'))}")
    lines.append(f"  {'File Size':<22} {fmt_size(ameta.get('filesize'))}")
    lines.append(f"\n  Stream URL (JWT):")
    lines.append(f"  {data.get('audio_download_url','(නැත)')}")
    lines.append(f"\n  Direct URL (Raw CDN):")
    lines.append(f"  {data.get('audio_direct_url','(නැත)')}")

    lines.append(f"\n{sep}")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


def save_test2(data: dict):
    """Save all formats with complete URLs to test2.txt"""
    path = os.path.join(SCRIPT_DIR, "test2.txt")
    formats = data.get("formats") or []
    lines = []
    sep = "=" * 80

    lines.append(sep)
    lines.append("  Syntiox DL-API — /info Response — test2.txt (All Formats + Full URLs)")
    lines.append(f"  Generated  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"  URL        : {TEST_URL}")
    lines.append(f"  Title      : {data.get('title','')}")
    lines.append(f"  Total Fmts : {len(formats)}")
    lines.append(sep)

    for i, fmt in enumerate(formats, 1):
        res    = fmt.get("res", "?")
        ext    = fmt.get("ext", "?")
        fid    = fmt.get("id", "?")
        dl_url = fmt.get("download_url", "(නැත)")
        di_url = fmt.get("direct_url", "(නැත)")

        lines.append(f"\n{'─'*80}")
        lines.append(f"  Format #{i}   |  ID: {fid}   |  Resolution: {res}   |  Ext: {ext}")
        lines.append(f"{'─'*80}")
        lines.append(f"  Stream URL (JWT — /stream?token=...):")
        lines.append(f"  {dl_url}")
        lines.append(f"\n  Direct URL (Raw CDN):")
        lines.append(f"  {di_url}")

    lines.append(f"\n{'='*80}")
    lines.append(f"  End of Formats  ({len(formats)} total)")
    lines.append(f"{'='*80}")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print()
    print(f"{C.MAGENTA}{C.BOLD}{'═'*70}")
    print(f"   🎵  Syntiox DL-API  ·  /info Endpoint Test")
    print(f"{'═'*70}{C.RESET}")
    print(f"  {C.DIM}URL :{C.RESET} {C.CYAN}{TEST_URL}{C.RESET}")
    print(f"  {C.DIM}Host:{C.RESET} {C.CYAN}{BASE_URL}{C.RESET}")

    # ── Request ──────────────────────────────────────────────────────────────
    print(f"\n  {C.DIM}⏳ Request යවනවා...{C.RESET}")
    body = json.dumps({"url": TEST_URL}).encode("utf-8")
    req  = urllib.request.Request(
        f"{BASE_URL}/info",
        data=body,
        headers={"Content-Type": "application/json", "x-api-key": API_KEY},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"\n  {C.RED}✘ HTTP Error {e.code}: {e.reason}{C.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n  {C.RED}✘ Error: {e}{C.RESET}")
        sys.exit(1)

    if data.get("type") == "error":
        print(f"\n  {C.RED}✘ API Error: {data.get('message')}{C.RESET}")
        sys.exit(1)

    print(f"  {C.GREEN}✔ Response ලැබුණා!{C.RESET}")

    # ════════════════ Console Display (shortened) ════════════════

    section("📋  මූලික තොරතුරු", C.CYAN)
    field("Title",        data.get("title"),           C.WHITE)
    field("Platform",     data.get("extractor",""),    C.YELLOW)
    field("Duration",     data.get("duration_string"), C.GREEN, f"({data.get('duration','')}s)")
    field("Uploader",     data.get("uploader"),        C.WHITE)
    field("Channel",      data.get("channel"),         C.WHITE)
    field("Channel URL",  shorten_url(data.get("channel_url","")), C.BLUE)
    field("Language",     data.get("language"),        C.WHITE)
    field("Age Limit",    data.get("age_limit"),       unit="+ වයස")
    field("Live",         data.get("is_live"))
    field("Was Live",     data.get("was_live"))

    section("📊  ස්ටැට්ස්", C.GREEN)
    field("Views",          data.get("view_count"),    unit="views")
    field("Likes",          data.get("like_count"),    unit="likes")
    field("Dislikes",       data.get("dislike_count"), unit="dislikes")
    field("Comments",       data.get("comment_count"), unit="comments")
    field("Average Rating", data.get("average_rating"))
    field("Upload Date",    fmt_date(data.get("upload_date","")), C.YELLOW)

    section("🏷️  Tags & Categories", C.MAGENTA)
    cats = data.get("categories") or []
    tags = data.get("tags") or []
    field("Categories", ", ".join(cats) if cats else None, C.YELLOW)
    field("Tags", f"{len(tags)} tags (test1.txt බලන්න full list)", C.DIM)

    section("📝  Description", C.BLUE)
    desc = (data.get("description") or "").strip()
    for line in desc.splitlines()[:5]:
        print(f"  {C.DIM}│{C.RESET} {C.WHITE}{line[:100]}{C.RESET}")
    if len(desc.splitlines()) > 5:
        print(f"  {C.DIM}│ ... (test1.txt බලන්න full){C.RESET}")

    section("🎬  Best Video", C.YELLOW)
    meta = data.get("best_video_meta") or {}
    field("Resolution", f"{meta.get('width')}x{meta.get('height')} @ {meta.get('fps','')}fps", C.GREEN)
    field("Codec",      f"{meta.get('vcodec')} / {meta.get('acodec')}", C.DIM)
    field("Ext",        meta.get("ext"), C.YELLOW)
    field("Size",       fmt_size(meta.get("filesize")))
    field("Stream URL", shorten_url(data.get("best_video_download_url",""), 55), C.CYAN)
    field("Direct URL", shorten_url(data.get("best_video_direct_url",""), 55),   C.BLUE)

    section("🎵  Best Audio", C.MAGENTA)
    ameta = data.get("audio_meta") or {}
    field("Bitrate",    ameta.get("abr"),         unit="kbps")
    field("Codec",      ameta.get("acodec"),      C.DIM)
    field("Ext",        ameta.get("ext"),         C.YELLOW)
    field("Size",       fmt_size(ameta.get("filesize")))
    field("Stream URL", shorten_url(data.get("audio_download_url",""), 55), C.CYAN)
    field("Direct URL", shorten_url(data.get("audio_direct_url",""), 55),   C.BLUE)

    section("📁  Formats Summary", C.CYAN)
    formats = data.get("formats") or []
    print(f"  {C.BOLD}{C.DIM}{'#':<4} {'ID':<12} {'Res':<10} {'Ext':<6} {'Direct URL'}{C.RESET}")
    hr()
    for i, fmt in enumerate(formats, 1):
        res  = fmt.get("res","?")
        ext  = fmt.get("ext","?")
        fid  = fmt.get("id","?")
        col  = C.GREEN if res.endswith("p") else C.MAGENTA
        dirurl = shorten_url(fmt.get("direct_url",""), 38)
        print(f"  {C.DIM}{i:<4}{C.RESET}{C.YELLOW}{fid:<12}{C.RESET}{col}{res:<10}{C.RESET}{C.DIM}{ext:<6}{C.RESET}{C.BLUE}{dirurl}{C.RESET}")

    print(f"\n  {C.DIM}Full URLs → test2.txt{C.RESET}")

    # ════════════════ Save to files ════════════════
    print()
    hr("═", color=C.GREEN)
    p1 = save_test1(data)
    p2 = save_test2(data)
    print(f"  {C.GREEN}{C.BOLD}✔  Files Saved!{C.RESET}")
    print(f"  {C.DIM}test1.txt{C.RESET} → {C.CYAN}{p1}{C.RESET}")
    print(f"  {C.DIM}test2.txt{C.RESET} → {C.CYAN}{p2}{C.RESET}")
    print(f"  {C.GREEN}{C.BOLD}✔  Formats: {len(formats)}{C.RESET}")
    hr("═", color=C.GREEN)
    print()

if __name__ == "__main__":
    main()
