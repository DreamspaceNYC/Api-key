from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from urllib.parse import urlparse, parse_qs
from typing import List

YOUTUBE_API_KEY = "AIzaSyD9-pgZDBpYk0Mz3j8MdERoaATq5fSg1tE"

app = FastAPI(title="ytlargeGPT")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    url: str

class AnalyzeResponse(BaseModel):
    title: str
    channelId: str
    channelTitle: str
    views: int
    uploadDate: str
    category: str
    tags: List[str]
    monetized: bool


class URLRequest(BaseModel):
    url: str


class Metadata(BaseModel):
    title: str
    uploadDate: str
    category: str
    views: int


class InfoResponse(BaseModel):
    monetized: bool
    authenticity: str
    estimatedEarnings: str
    tags: List[str]
    metadata: Metadata

def extract_video_id(url: str) -> str:
    parsed = urlparse(url)
    if parsed.hostname in ("youtu.be", "www.youtu.be"):
        return parsed.path.lstrip("/")
    if parsed.hostname in ("www.youtube.com", "youtube.com"):
        if parsed.path == "/watch":
            qs = parse_qs(parsed.query)
            return qs.get("v", [""])[0]
        if parsed.path.startswith("/embed/"):
            return parsed.path.split("/")[2]
    raise ValueError("Invalid YouTube URL")


@app.get("/")
async def health() -> dict:
    return {"status": "YTLarge GPT API is live!"}


@app.post("/ytlarge-info", response_model=InfoResponse)
async def ytlarge_info(req: URLRequest) -> InfoResponse:
    _ = req.url
    return InfoResponse(
        monetized=True,
        authenticity="high",
        estimatedEarnings="$123 - $456",
        tags=["AI", "YouTube", "Growth"],
        metadata=Metadata(
            title="Sample Video Title",
            uploadDate="2023-12-01",
            category="Education",
            views=120000,
        ),
    )

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest):
    try:
        video_id = extract_video_id(req.url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    async with httpx.AsyncClient() as client:
        video_resp = await client.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params={
                "part": "snippet,statistics,status",
                "id": video_id,
                "key": YOUTUBE_API_KEY,
            },
        )
        video_data = video_resp.json()
        items = video_data.get("items", [])
        if not items:
            raise HTTPException(status_code=404, detail="Video not found")
        video = items[0]
        snippet = video.get("snippet", {})
        statistics = video.get("statistics", {})
        status = video.get("status", {})
        channel_id = snippet.get("channelId")

        # Fetch channel status
        channel_resp = await client.get(
            "https://www.googleapis.com/youtube/v3/channels",
            params={
                "part": "status",
                "id": channel_id,
                "key": YOUTUBE_API_KEY,
            },
        )
        channel_items = channel_resp.json().get("items", [])
        channel_status = channel_items[0]["status"] if channel_items else {}

        # Fetch category title
        category_resp = await client.get(
            "https://www.googleapis.com/youtube/v3/videoCategories",
            params={
                "part": "snippet",
                "id": snippet.get("categoryId"),
                "key": YOUTUBE_API_KEY,
            },
        )
        category_items = category_resp.json().get("items", [])
        category = (
            category_items[0]["snippet"].get("title") if category_items else "Unknown"
        )

        monetized = bool(
            status.get("embeddable")
            and status.get("license") == "youtube"
            and channel_status.get("isLinked")
        )

        return AnalyzeResponse(
            title=snippet.get("title", ""),
            channelId=channel_id or "",
            channelTitle=snippet.get("channelTitle", ""),
            views=int(statistics.get("viewCount", 0)),
            uploadDate=snippet.get("publishedAt", "").split("T")[0],
            category=category,
            tags=snippet.get("tags", []),
            monetized=monetized,
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
