# Syntiox DL — REST API

YouTube video & audio direct URL generator API built with **FastAPI** + **yt-dlp**.  
This API retrieves raw stream URLs for YouTube videos/audio directly from YouTube without proxying the media files through the server. No local media storage or FFmpeg is required for downloads!

---

## 🚀 Quick Start

1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the server:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```

Or just double-click **`run_api.bat`**

Swagger UI → **http://localhost:8000/docs**

---

## 📡 Endpoints

### Health
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | API health check |
| `GET` | `/ffmpeg` | Check if ffmpeg is available (optional) |

### Info (Get Direct Stream URLs)
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/info` | Get video/playlist details + raw direct download links |

**Request:**
```json
{ "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ" }
```

**Response (video):**
```json
{
  "type": "video",
  "title": "Rick Astley - Never Gonna Give You Up",
  "thumb": "https://...",
  "duration": 212,
  "uploader": "Rick Astley",
  "best_video_download_url": "https://rr5---sn-...googlevideo.com/videoplayback?...",
  "audio_download_url": "https://rr5---sn-...googlevideo.com/videoplayback?...",
  "formats": [
    { 
      "id": "137", 
      "res": "1080p", 
      "ext": "mp4", 
      "url": "https://rr5---sn-...googlevideo.com/videoplayback?...", 
      "download_url": "https://rr5---sn-...googlevideo.com/videoplayback?..." 
    }
  ]
}
```

**Response (playlist):**
```json
{
  "type": "playlist",
  "title": "My Playlist",
  "count": 12,
  "videos": [
    { "title": "Song 1", "url": "https://..." }
  ]
}
```

---

## 🛠 Features

- **No Server Storage:** Files are downloaded directly from YouTube's CDN to the user's browser/client.
- **No FFmpeg Dependency:** Video and audio streams are directly accessed from YouTube CDN, removing the need for server-side audio conversion or format merging.
- **Bypasses IP Locks:** Emulates Android & iOS player clients to bypass YouTube's strict IP locking mechanism.

---

## 📁 Folder Structure

```
├── app.py            ← FastAPI routes
├── engine.py         ← yt-dlp direct stream extractor
├── requirements.txt  ← Python dependencies
├── run_api.bat       ← One-click Windows start script
└── README.md         ← This file
```
