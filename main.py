from fastapi import FastAPI, HTTPException
from googleapiclient.discovery import build
import os

app = FastAPI()

# YouTube API setup
API_KEY = "AIzaSyD9-pgZDBpYk0Mz3j8MdERoaATq5fSg1tE"
youtube = build("youtube", "v3", developerKey=API_KEY)

# Monetization Checker
@app.get("/monetization")
async def check_monetization(video_id: str):
    try:
        request = youtube.videos().list(part="status", id=video_id)
        response = request.execute()
        if not response["items"]:
            return {"error": "Video not found"}
        return {"video_id": video_id, "monetized": response["items"][0]["status"]["license"] == "youtube"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# YouTube ID Finder
@app.get("/idfinder")
async def find_id(channel_url: str):
    try:
        # Extract channel ID from URL (simplified logic)
        channel_id = channel_url.split("channel/")[-1].split("?")[0]
        request = youtube.channels().list(part="snippet", id=channel_id)
        response = request.execute()
        return {"channel_id": channel_id, "title": response["items"][0]["snippet"]["title"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Data Viewer
@app.get("/dataviewer")
async def get_data(video_id: str):
    try:
        request = youtube.videos().list(part="statistics,snippet", id=video_id)
        response = request.execute()
        if not response["items"]:
            return {"error": "Video not found"}
        item = response["items"][0]
        return {
            "title": item["snippet"]["title"],
            "view_count": item["statistics"].get("viewCount", "N/A"),
            "like_count": item["statistics"].get("likeCount", "N/A")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Tag Extractor
@app.get("/tagsextractor")
async def get_tags(video_id: str):
    try:
        request = youtube.videos().list(part="snippet", id=video_id)
        response = request.execute()
        if not response["items"]:
            return {"error": "Video not found"}
        tags = response["items"][0]["snippet"].get("tags", [])
        return {"video_id": video_id, "tags": tags}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Money Calculator (simplified estimate)
@app.get("/moneycalculator")
async def calculate_money(video_id: str):
    try:
        request = youtube.videos().list(part="statistics", id=video_id)
        response = request.execute()
        if not response["items"]:
            return {"error": "Video not found"}
        views = int(response["items"][0]["statistics"]["viewCount"])
        # Rough estimate: $0.25-$4 per 1000 views
        revenue = views * 0.0025  # Low-end estimate
        return {"video_id": video_id, "estimated_revenue_usd": round(revenue, 2)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Shadowban Detector (simplified check via view consistency)
@app.get("/shadowbandetector")
async def check_shadowban(video_id: str):
    try:
        request = youtube.videos().list(part="statistics", id=video_id)
        response = request.execute()
        if not response["items"]:
            return {"error": "Video not found"}
        views = int(response["items"][0]["statistics"]["viewCount"])
        # Placeholder logic: Shadowban if views are unusually low for upload date
        return {"video_id": video_id, "shadowbanned": views < 10}  # Dummy threshold
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Image Downloader (returns URL placeholders)
@app.get("/imagedownloader")
async def get_images(video_id: str):
    try:
        request = youtube.videos().list(part="snippet", id=video_id)
        response = request.execute()
        if not response["items"]:
            return {"error": "Video not found"}
        snippet = response["items"][0]["snippet"]
        return {
            "thumbnail_url": snippet["thumbnails"]["default"]["url"],
            "channel_profile_url": "N/A"  # Requires channel ID lookup
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))