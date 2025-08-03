from flask import Flask, request, jsonify
from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs
import re
import os

app = Flask(__name__)

# YouTube API setup (replace with your API key)
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY', 'YOUR_API_KEY_HERE')
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

def get_video_stats(video_id):
    """Fetch video stats using YouTube API."""
    try:
        response = youtube.videos().list(
            part='snippet,statistics,contentDetails',
            id=video_id
        ).execute()
        if not response['items']:
            return {'error': 'Video not found'}
        item = response['items'][0]
        duration = item['contentDetails'].get('duration', 'PT0S')
        # Basic authenticity check: short duration or specific tags may indicate non-original content
        is_original = not ('shorts' in item['snippet'].get('tags', []) or 'PT1M' in duration)
        return {
            'title': item['snippet']['title'],
            'views': item['statistics'].get('viewCount', '0'),
            'likes': item['statistics'].get('likeCount', '0'),
            'comments': item['statistics'].get('commentCount', '0'),
            'published_at': item['snippet']['publishedAt'],
            'is_original': is_original
        }
    except Exception as e:
        return {'error': str(e)}

def get_channel_stats(channel_id):
    """Fetch channel stats and estimate monetization."""
    try:
        response = youtube.channels().list(
            part='snippet,statistics',
            id=channel_id
        ).execute()
        if not response['items']:
            return {'error': 'Channel not found'}
        item = response['items'][0]
        subscribers = int(item['statistics'].get('subscriberCount', '0'))
        total_views = int(item['statistics'].get('viewCount', '0'))
        video_count = int(item['statistics'].get('videoCount', '0'))
        # Estimate watch hours (rough: total views * average 5 min video / 60)
        watch_hours = (total_views * 5) / 60
        # Monetization eligibility: 1,000 subs, 4,000 watch hours
        is_monetized = subscribers >= 1000 and watch_hours >= 4000
        return {
            'title': item['snippet']['title'],
            'subscribers': str(subscribers),
            'video_count': str(video_count),
            'total_views': str(total_views),
            'estimated_watch_hours': str(round(watch_hours)),
            'is_monetized': is_monetized
        }
    except Exception as e:
        return {'error': str(e)}

def process_prompt(data, prompt):
    """Process natural language prompt."""
    if not prompt:
        return data
    prompt = prompt.lower()
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
    data = request.get_json()
    video_url = data.get('video_url', '')
    channel_id = data.get('channel_id', '')
    prompt = data.get('prompt', '')

    if video_url:
        video_id = extract_video_id(video_url)
        if not video_id:
            return jsonify({'error': 'Invalid video URL'}), 400
        result = get_video_stats(video_id)
    elif channel_id:
        channel_id = extract_channel_id(channel_id)
        if not channel_id:
            return jsonify({'error': 'Invalid channel ID or URL'}), 400
        result = get_channel_stats(channel_id)
    else:
        return jsonify({'error': 'Provide video_url or channel_id'}), 400

    if result.get('error'):
        return jsonify(result), 404

    # Process natural language prompt
    result = process_prompt(result, prompt)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))