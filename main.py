import os, re, time, logging, json
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_caching import Cache
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
cache = Cache(app, config={"CACHE_TYPE": "simple", "CACHE_DEFAULT_TIMEOUT": 3600})

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
PORT = int(os.getenv("PORT", 8080))
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

# ---------- helpers ----------
def extract_video_id(url: str) -> str | None:
    """Return videoId from classic or short URL"""
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",
        r"(?:youtu\.be\/)([0-9A-Za-z_-]{11})"
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None

def safe_int(x):
    return int(x) if str(x).isdigit() else 0

def exponential_backoff(attempt):
    return 2 ** attempt + 1

def yt_call(func, *args, **kwargs):
    """3-attempt retry with exponential backoff"""
    for attempt in range(3):
        try:
            return func(*args, **kwargs).execute()
        except HttpError as e:
            if e.resp.status in [403, 429]:
                if attempt == 2:
                    raise
                time.sleep(exponential_backoff(attempt))
            else:
                raise

# ---------- core ----------
@cache.memoize()
def fetch_video_stats(video_id: str):
    resp = yt_call(
        youtube.videos().list,
        part="snippet,statistics,contentDetails",
        id=video_id
    )
    if not resp["items"]:
        raise ValueError("Video not found")
    v = resp["items"][0]
    return {
        "title": v["snippet"]["title"],
        "published_at": v["snippet"]["publishedAt"],
        "views": safe_int(v["statistics"].get("viewCount")),
        "likes": safe_int(v["statistics"].get("likeCount")),
        "comments": safe_int(v["statistics"].get("commentCount")),
        "duration": v["contentDetails"]["duration"],
        "channel_id": v["snippet"]["channelId"]
    }

@cache.memoize()
def fetch_channel_stats(channel_id: str):
    resp = yt_call(
        youtube.channels().list,
        part="snippet,statistics,contentDetails",
        id=channel_id
    )
    if not resp["items"]:
        raise ValueError("Channel not found")
    c = resp["items"][0]
    subs = safe_int(c["statistics"].get("subscriberCount"))
    vids = safe_int(c["statistics"].get("videoCount"))
    total_views = safe_int(c["statistics"].get("viewCount"))
    # rough watch-hours = total_views * 3 min avg
    watch_hours = int(total_views * 3 / 60)
    monetized = subs >= 1000 and watch_hours >= 4000
    return {
        "title": c["snippet"]["title"],
        "subscribers": subs,
        "video_count": vids,
        "total_views": total_views,
        "estimated_watch_hours": watch_hours,
        "monetization_status": "eligible" if monetized else "not_eligible"
    }

# ---------- prompt NLP ----------
def resolve_prompt(prompt: str, data: dict) -> dict:
    prompt = prompt.lower()
    if "monetiz" in prompt or "eligible" in prompt:
        return {"monetization_status": data.get("monetization_status")}
    if "subscribers" in prompt or "subs" in prompt:
        return {"subscribers": data.get("subscribers")}
    if "views" in prompt and "total" not in prompt:
        return {"views": data.get("views")}
    if "total views" in prompt:
        return {"total_views": data.get("total_views")}
    if "videos" in prompt or "uploads" in prompt:
        return {"video_count": data.get("video_count")}
    return data  # fallback: full object

# ---------- route ----------
@app.post("/youtube-monetization")
def monetization_endpoint():
    payload = request.get_json(force=True, silent=True) or {}
    video_url = payload.get("video_url")
    channel_id = payload.get("channel_id")
    prompt = payload.get("prompt")

    if not video_url and not channel_id:
        return jsonify(error="Provide video_url or channel_id"), 400

    try:
        if video_url:
            video_id = extract_video_id(video_url)
            if not video_id:
                return jsonify(error="Invalid YouTube URL"), 400
            data = fetch_video_stats(video_id)
            channel_id = data["channel_id"]  # cascade to channel stats
        if channel_id:
            data = fetch_channel_stats(channel_id)
        if prompt:
            data = resolve_prompt(prompt, data)
        return jsonify(data)
    except ValueError as e:
        return jsonify(error=str(e)), 404
    except Exception as e:
        logger.exception(e)
        return jsonify(error="Internal API error"), 500

# ---------- health ----------
@app.get("/")
def ping():
    return "ok"

if __name__ == "__main__":
    app.run(port=PORT)
