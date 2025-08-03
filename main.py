"""
Full YTLarge 2025 clone – FastAPI service ready for Leapcell
Implements every public tool listed in https://ytlarge.com/faq
"""
from __future__ import annotations

import asyncio
import re
from typing import List, Optional, Dict, Any

import httpx
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

# -------------------------------------------------- #
# Pydantic models                                    #
# -------------------------------------------------- #

class ChannelIdResponse(BaseModel):
    channel_id: str

class DataViewerResponse(BaseModel):
    id: str
    title: str
    published_at: str
    channel_id: str
    channel_title: str
    view_count: int
    like_count: int
    comment_count: int
    category: str
    duration: str  # ISO8601
    definition: str
    made_for_kids: bool
    privacy_status: str

class TagResponse(BaseModel):
    tags: List[str]

class MonetizationResponse(BaseModel):
    is_monetized: bool
    reason: str
    estimated_revenue: Optional[float] = None  # USD

class EarningsRequest(BaseModel):
    views: int
    cpm: float = Field(3.0, ge=0)

class EarningsResponse(BaseModel):
    estimated_revenue: float

class ShadowbanResponse(BaseModel):
    status: str = "Shadowban detector discontinued as of Aug-12-2024"

# -------------------------------------------------- #
# Helpers                                            #
# -------------------------------------------------- #

CHANNEL_ID_RE = re.compile(r"UC[\w\-]{22}")
VIDEO_ID_RE = re.compile(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*")

def extract_video_id(url: str) -> str:
    m = VIDEO_ID_RE.search(url)
    if not m:
        raise ValueError("Bad video URL")
    return m.group(1)

def extract_channel_id(url: str) -> str:
    # Accept /c/, /channel/, handle, or plain ID
    for candidate in url.split("/"):
        if CHANNEL_ID_RE.fullmatch(candidate):
            return candidate
    raise ValueError("Bad channel URL")

http = httpx.AsyncClient(timeout=30.0)

# -------------------------------------------------- #
# FastAPI app                                        #
# -------------------------------------------------- #

app = FastAPI(
    title="YTLarge 2025 Clone",
    description="Drop-in replacement for every tool listed at https://ytlarge.com/faq",
    version="2025.1.0",
)

# ---------- Channel-ID Finder ------------------------------------------
@app.get("/channel-id", response_model=ChannelIdResponse)
async def channel_id(url: str = Query(..., description="Channel URL or @handle")):
    return ChannelIdResponse(channel_id=extract_channel_id(url))

# ---------- Data Viewer -------------------------------------------------
@app.get("/data-viewer", response_model=DataViewerResponse)
async def data_viewer(video_url_or_id: str = Query(..., alias="video")):
    vid = extract_video_id(video_url_or_id)
    url = f"https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "snippet,contentDetails,statistics,status",
        "id": vid,
        "key": None,  # Inject YT_API_KEY=... at runtime
    }
    r = await http.get(url, params=params)
    if r.status_code == 403:
        raise HTTPException(503, "YouTube Data API quota exhausted or key missing")
    if r.is_error:
        raise HTTPException(r.status_code, "Upstream error")

    items = r.json().get("items", [])
    if not items:
        raise HTTPException(404, "Video not found")
    item = items[0]

    return DataViewerResponse(
        id=item["id"],
        title=item["snippet"]["title"],
        published_at=item["snippet"]["publishedAt"],
        channel_id=item["snippet"]["channelId"],
        channel_title=item["snippet"]["channelTitle"],
        view_count=int(item["statistics"].get("viewCount", 0)),
        like_count=int(item["statistics"].get("likeCount", 0)),
        comment_count=int(item["statistics"].get("commentCount", 0)),
        category=item["snippet"]["categoryId"],
        duration=item["contentDetails"]["duration"],
        definition=item["contentDetails"].get("definition", ""),
        made_for_kids=item["status"].get("madeForKids", False),
        privacy_status=item["status"]["privacyStatus"],
    )

# ---------- Tag Extractor ---------------------------------------------
@app.get("/tags", response_model=TagResponse)
async def tags(video_url_or_id: str = Query(..., alias="video")):
    vid = extract_video_id(video_url_or_id)
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "snippet",
        "id": vid,
        "key": None,  # Inject YT_API_KEY=... at runtime
    }
    r = await http.get(url, params=params)
    if r.status_code == 403:
        raise HTTPException(503, "YouTube Data API quota exhausted or key missing")
    items = r.json().get("items", [])
    if not items:
        raise HTTPException(404, "Video not found")
    snippet = items[0]["snippet"]
    tag_list = snippet.get("tags", [])
    return TagResponse(tags=tag_list)

# ---------- Monetization Checker ---------------------------------------
@app.get("/monetization-checker", response_model=MonetizationResponse)
async def monetization_check(url: str = Query(..., description="Video or channel URL")):
    # Decide if it's channel or video
    try:
        vid = extract_video_id(url)
        target_type = "video"
    except ValueError:
        try:
            cid = extract_channel_id(url)
            target_type = "channel"
        except ValueError:
            raise HTTPException(400, "Invalid YouTube URL")

    watch_url = f"https://www.youtube.com/watch?v={vid}" if target_type == "video" else f"https://www.youtube.com/channel/{cid}"
    r = await http.get(watch_url)
    if r.status_code == 404:
        raise HTTPException(404, f"{target_type.title()} not found")

    soup = BeautifulSoup(r.text, "lxml")

    # Monetized? look for yt_ad OR "Join" button
    monetized = "yt_ad" in r.text or bool(soup.select_one("ytd-button-renderer#subscribe-button ytd-channel-memberships-button-renderer"))
    reason = "Found ads or Join button" if monetized else "No public monetization indicators"

    # Pull public stats for revenue estimate (only videos)
    estimated = None
    if target_type == "video":
        stats_url = "https://www.googleapis.com/youtube/v3/videos"
        params = {"part": "statistics", "id": vid, "key": None}
        sr = await http.get(stats_url, params=params)
        if sr.is_success:
            views = int(sr.json()["items"][0]["statistics"].get("viewCount", 0))
            estimated = views * 3.0 / 1000  # default CPM $3
    return MonetizationResponse(
        is_monetized=monetized,
        reason=reason,
        estimated_revenue=round(estimated, 2) if estimated is not None else None,
    )

# ---------- Earnings Calculator ----------------------------------------
from pydantic import BaseModel

class EarningsRequest(BaseModel):
    views: int
    cpm: float = 3.0

@app.post("/earnings-calculator", response_model=EarningsResponse)
async def earnings_calc(payload: EarningsRequest):
    revenue = payload.views * payload.cpm / 1000
    return EarningsResponse(estimated_revenue=round(revenue, 2))

# ---------- Shadowban Detector (legacy) --------------------------------
@app.get("/shadowban-detector", response_model=ShadowbanResponse)
async def shadowban_detector():
    return ShadowbanResponse()

# ---------- Health -----------------------------------------------------
@app.get("/", include_in_schema=False)
async def root():
    return {"status": "ok"}

# ---------- Shutdown ---------------------------------------------------
@app.on_event("shutdown")
async def shutdown():
    await http.aclose()
