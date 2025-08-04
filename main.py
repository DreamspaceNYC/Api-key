from flask import Flask, request, jsonify
from flask_caching import Cache
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from urllib.parse import urlparse, parse_qs
import re
import os
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, filename='app.log')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure caching
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})

# YouTube API setup
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
if not YOUTUBE_API_KEY:
    raise ValueError("YOUTUBE_API_KEY environment variable is required")
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

def extract_video_id(url):
    """Extract video ID from YouTube URL."""
    if not url:
        return None
    parsed = urlparse(url)
    if parsed.hostname in ('youtu.be', 'www.youtu.be'):
        return parsed.path.lstrip('/')
    if parsed.hostname in ('www.youtube.com', 'youtube.com'):
        if parsed.path == '/watch':
            return parse_qs(parsed.query).get('v', [None])[0]
        if parsed.path.startswith('/embed/'):
            return parsed.path.split('/')[2]
    return None

def extract_channel_id(channel_input):
    """Extract channel ID from input (URL or ID)."""
    if channel_input.startswith('UC') and len(channel_input) == 24:
        return channel_input
    match = re.match(r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/(?:channel\/|user\/)?([a-zA-Z0-9_-]{24})', channel_input)
    return match.group(1) if match else None

@cache.memoize(timeout=3600)  # Cache for 1 hour
def get_video_stats(video_id):
    """Fetch video stats using YouTube API with retry logic."""
    logger.info(f"Fetching stats for video_id: {video_id}")
    try:
        for attempt in range(3):
            try:
                response = youtube.videos().list(
                    part='snippet,statistics,contentDetails',
                    id=video_id
                ).execute()
                if not response['items']:
                    logger.warning(f"Video not found: {video_id}")
                    return {'error': 'Video not found'}
                item = response['items'][0]
                duration = item['contentDetails'].get('duration', 'PT0S')
                is_original = not ('shorts' in item['snippet'].get('tags', []) or 'PT1M' in duration)
                return {
                    'title': item['snippet']['title'],
                    'views': item['statistics'].get('viewCount', '0'),
                    'likes': item['statistics'].get('likeCount', '0'),
                    'comments': item['statistics'].get('commentCount', '0'),
                    'published_at': item['snippet']['publishedAt'],
                    'is_original': is_original
                }
            except HttpError as e:
                if 'quotaExceeded' in str(e):
                    logger.warning(f"Quota exceeded for video_id: {video_id}, retrying...")
                    time.sleep(2 ** attempt)
                    continue
                logger.error(f"Error fetching video stats: {str(e)}")
                raise
    except Exception as e:
        logger.error(f"Unexpected error for video_id: {video_id}: {str(e)}")
        return {'error': str(e)}

@cache.memoize(timeout=3600)  # Cache for 1 hour
def get_channel_stats(channel_id):
    """Fetch channel stats and estimate monetization with retry logic."""
    logger.info(f"Fetching stats for channel_id: {channel_id}")
    try:
        for attempt in range(3):
            try:
                response = youtube.channels().list(
                    part='snippet,statistics',
                    id=channel_id
                ).execute()
                if not response['items']:
                    logger.warning(f"Channel not found: {channel_id}")
                    return {'error': 'Channel not found'}
                item = response['items'][0]
                subscribers = int(item['statistics'].get('subscriberCount', '0'))
                total_views = int(item['statistics'].get('viewCount', '0'))
                video_count = int(item['statistics'].get('videoCount', '0'))
                watch_hours = (total_views * 5) / 60
                is_monetized = subscribers >= 1000 and watch_hours >= 4000
                return {
                    'title': item['snippet']['title'],
                    'subscribers': str(subscribers),
                    'video_count': str(video_count),
                    'total_views': str(total_views),
                    'estimated_watch_hours': str(round(watch_hours)),
                    'is_monetized': is_monetized
                }
            except HttpError as e:
                if 'quotaExceeded' in str(e):
                    logger.warning(f"Quota exceeded for channel_id: {channel_id}, retrying...")
                    time.sleep(2 ** attempt)
                    continue
                logger.error(f"Error fetching channel stats: {str(e)}")
                raise
    except Exception as e:
        logger.error(f"Unexpected error for channel_id: {channel_id}: {str(e)}")
        return {'error': str(e)}

def process_prompt(data, prompt):
    """Process natural language prompt."""
    if not prompt:
        return data
    prompt = prompt.lower()
    logger.info(f"Processing prompt: {prompt}")
    if 'monetized' in prompt or 'monetization' in prompt:
        return {'is_monetized': data.get('is_monetized', False)}
    elif 'original' in prompt or 'authenticity' in prompt:
        return {'is_original': data.get('is_original', True)}
    elif 'views' in prompt:
        return {'views': data.get('views', data.get('total_views', '0'))}
    elif 'subscribers' in prompt:
        return {'subscribers': data.get('subscribers', '0')}
    elif 'likes' in prompt:
        return {'likes': data.get('likes', '0')}
    return data

@app.route('/youtube-monetization', methods=['POST'])
def youtube_monetization():
    logger.info("Received request to /youtube-monetization")
    data = request.get_json()
    video_url = data.get('video_url', '')
    channel_id = data.get('channel_id', '')
    prompt = data.get('prompt', '')

    if video_url:
        video_id = extract_video_id(video_url)
        if not video_id:
            logger.warning(f"Invalid video URL: {video_url}")
            return jsonify({'error': 'Invalid video URL'}), 400
        result = get_video_stats(video_id)
    elif channel_id:
        channel_id = extract_channel_id(channel_id)
        if not channel_id:
            logger.warning(f"Invalid channel ID or URL: {channel_id}")
            return jsonify({'error': 'Invalid channel ID or URL'}), 400
        result = get_channel_stats(channel_id)
    else:
        logger.warning("Missing video_url or channel_id")
        return jsonify({'error': 'Provide video_url or channel_id'}), 400

    if result.get('error'):
        logger.error(f"Error in result: {result['error']}")
        return jsonify(result), 404

    result = process_prompt(result, prompt)
    logger.info(f"Returning result: {result}")
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
