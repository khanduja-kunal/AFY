# Fastapi-Youtube-Downloader

This is a **FastAPI** based web application that allows users to download videos and audio from platforms like **YouTube**. The API supports various formats (MP4, MKV, MP3, WebM) and qualities (360p, 480p, 720p, 1080p, 4K). Additionally, the API can fetch metadata for videos without downloading them.

---

## Features

- **Download Videos and Audio**: Users can download videos and audio in different formats like `mp4`, `mkv`, `mp3`, and `webm`.
- **Quality Selection**: Users can specify the quality of videos (`360p`, `480p`, `720p`, `1080p`, `4k`).
- **Metadata Fetching**: Users can get metadata for a video, such as title, duration, views, etc.
- **Automatic Fallback**: If a download fails using `yt-dlp`, the system will fall back to `pytube` for the download.
- **Retry Logic**: The application retries downloading up to 3 times if there’s an error with the download process.
- **Asynchronous Task Processing**: Uses Celery with Redis broker to handle background download tasks.
- **Download History Tracking**: Stores each download attempt with status and timestamp in a database.

---

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/khanduja-kunal/Fastapi-Youtube-Downloader.git
   cd Fastapi-Youtube-Downloader
   ```

2. **Install the required dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

1. **Start Redis Server**:

   ```bash
   redis-server
   ```

2. **Run the Celery worker**:

   ```bash
   celery -A app.worker.download_task.celery worker --loglevel=info
   ```

3. **Run the FastAPI application**:

   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://127.0.0.1:8000`.

4. **Available Endpoints**:

   ### `POST /download/`

   Initiate a video or audio download task.

   **Request Body**:
   ```json
   {
     "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
     "format": "mp4",
     "quality": "720p"
   }
   ```

   **Response**:
   ```json
   {
     "message": "Download started",
     "task_id": "7c8a7b4e-f122-4c26-85d9-abcde1234567"
   }
   ```

   ### `GET /metadata`

   Fetch metadata for a given video URL.

   **Query Parameters**:
   - `url`: Required, the URL of the video.

   **Response**:
   ```json
   {
     "title": "WILD WORLD DOLBY VISION™ | EXTREME COLORS [8K HDR]",
     "duration": 2684,
     "channel": "8K Paradise",
     "thumbnail": "https://i.ytimg.com/vi_webp/Rwe5Aw3KPHY/maxresdefault.webp",
     "published_date": "20231229",
     "views": 25893772,
     "likes": 101469,
     "size": 16560874749
   }
   ```

   ### `GET /history`

   Fetch history/logs from the database.

---

## Example Requests

### Download Video Example (using `curl`):
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/download/' \
  -H 'Content-Type: application/json' \
  -d '{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "format": "mp4",
  "quality": "1080p"
}'
```

### Fetch Metadata Example (using `curl`):
```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/metadata?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ'
```

---

## Dependencies

- **FastAPI**: Web framework for building APIs.
- **yt-dlp**: A powerful command-line tool for downloading videos from YouTube and other sites.
- **pytube**: A lightweight Python library for downloading YouTube content.
- **uvicorn**: ASGI server for running FastAPI apps.
- **Celery**: Task queue for asynchronous background task processing.
- **Redis**: Message broker for Celery.
- **SQLAlchemy**: ORM for database interactions.

---

## Directory Structure

```
Fastapi_Youtube_Downloader/
├── app/                       # FastAPI application code
│   ├── api/                   # API endpoint handlers
│   │   ├── __init__.py
│   │   ├── download.py
│   │   ├── history.py
│   │   └── metadata.py
│   ├── core/                  # Core configuration and security
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── rate_limit.py
│   │   ├── redis_client.py
│   │   └── security.py
│   ├── db/                    # Database models and setup
│   │   ├── __init__.py
│   │   ├── init_db.py
│   │   ├── session.py
│   │   └── models.py
│   ├── services/              # Business logic
│   │   ├── __init__.py
│   │   ├── downloader.py
│   ├── worker/                # Background tasks with Celery
│   │   ├── __init__.py
│   │   └── download_task.py
│   ├── utils/                 # Helper functions
│   │   ├── __init__.py
│   │   └── validation.py
│   ├── __init__.py
│   └── main.py                # Entry point for FastAPI app
├── downloads/                 # Stores downloaded files
├── AFY/                       # Virtual environment (ignored in VCS)
├── .env                       # Environment configuration
├── .gitignore                 # Git ignore rules
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation
```

---

## Contributing

Feel free to fork this project, make changes, and create a pull request with your improvements!

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

# Fastapi-Youtube-Downloader