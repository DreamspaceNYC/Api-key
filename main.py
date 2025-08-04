from fastapi import FastAPI, HTTPException
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, HttpUrl
import googleapiclient.discovery
import googleapiclient.errors
import os
import re
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
import isodate

load_dotenv()

app = FastAPI(
    title="YouTube Video Analysis API",
    description="API to fetch detailed YouTube video metadata, mimicking ytlarge.com, for ChatGPT Custom GPT Action.",
    version="1.0.0"
)

# YouTube API setup
API_KEY = os.getenv("YOUTUBE_API_KEY")
if not API_KEY:
    raise Exception("YOUTUBE_API_KEY not set in .env")
youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=API_KEY)

# Pydantic model for request
class VideoRequest(BaseModel):
    video_url: HttpUrl

# Pydantic model for response
class VideoResponse(BaseModel):
    video_id: str
    title: str
    channel_title: str
    upload_date: str
    views: int
    likes: int
    comments: int
    description: str
    thumbnail_url: str
    duration: str
    tags: list[str]
    category_id: str
    channel_id: str

# Extract video ID from URL or ID
def extract_video_id(video_input: str) -> str:
    # Handle direct video ID
    if re.match(r'^[0-9A-Za-z_-]{11}$', video_input):
        return video_input
    # Parse URL
    parsed = urlparse(video_input)
    if parsed.hostname in ('www.youtube.com', 'youtube.com', 'youtu.be'):
        if parsed.hostname == 'youtu.be':
            return parsed.path[1:]
        query = parse_qs(parsed.query)
        return query.get('v', [None])[0]
    raise HTTPException(status_code=400, detail="Invalid YouTube video URL or ID")

@app.get("/")
async def root():
    return {"message": "YouTube Video Analysis API"}

@app.post("/video-stats", response_model=VideoResponse)
async def get_video_stats(request: VideoRequest):
    try:
        video_id = extract_video_id(request.video_url)
        if not video_id:
            raise HTTPException(status_code=400, detail="Could not extract video ID")

        # Call YouTube API
        yt_request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=video_id
        )
        response = yt_request.execute()

        if not response.get("items"):
            raise HTTPException(status_code=404, detail="Video not found")

        video_data = response["items"][0]
        snippet = video_data["snippet"]
        stats = video_data["statistics"]
        content_details = video_data["contentDetails"]

        return {
            "video_id": video_id,
            "title": snippet.get("title", "N/A"),
            "channel_title": snippet.get("channelTitle", "N/A"),
            "upload_date": snippet.get("publishedAt", "N/A"),
            "views": int(stats.get("viewCount", 0)),
            "likes": int(stats.get("likeCount", 0)),
            "comments": int(stats.get("commentCount", 0)),
            "description": snippet.get("description", "N/A"),
            "thumbnail_url": snippet["thumbnails"].get("high", {}).get("url", "N/A"),
            "duration": str(isodate.parse_duration(content_details.get("duration", "PT0S"))),
            "tags": snippet.get("tags", []),
            "category_id": snippet.get("categoryId", "N/A"),
            "channel_id": snippet.get("channelId", "N/A")
        }
    except googleapiclient.errors.HttpError as e:
        raise HTTPException(status_code=500, detail=f"YouTube API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

# Custom OpenAPI schema for GPT Action
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="YouTube Video Analysis API",
        version="1.0.0",
        description="API to fetch detailed YouTube video metadata, mimicking ytlarge.com, for ChatGPT Custom GPT Action.",
        routes=app.routes,
    )
    openapi_schema["openapi"] = "3.1.0"
    openapi_schema["servers"] = [{"url": "https://your-leapcell-app.leapcell.io"}]  # Update after deployment
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
