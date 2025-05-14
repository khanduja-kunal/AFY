from fastapi import APIRouter, HTTPException, status
import yt_dlp

router = APIRouter()

@router.get("/metadata")
async def get_metadata(url: str):
    try:
        with yt_dlp.YoutubeDL({'quiet': True, 'noplaylist': True}) as ydl:
            data = ydl.extract_info(url, download=False)
            return {
                "title": data.get("title", "N/A"),
                "duration": data.get("duration", "N/A"),
                "channel": data.get("uploader", "N/A"),
                "thumbnail": data.get("thumbnail", "N/A"),
                "published_date": data.get("upload_date", "N/A"),
                "views": data.get("view_count", "N/A"),
                "likes": data.get("like_count", "N/A"),
                "size": data.get("filesize") or data.get("filesize_approx")
            }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Metadata fetch failed: {str(e)}")
