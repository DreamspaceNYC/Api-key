# YouTube Monetization and Analytics API

This project provides a Flask-based API that replicates the core functionality of `ytlarge.com`, allowing users to check the monetization status and analytics of YouTube videos or channels. The API accepts a YouTube video URL or channel ID along with an optional natural language prompt (e.g., "Is this monetized?" or "Get subscribers") and returns JSON responses. It is designed to be deployed on LeapCell and integrated as a Custom GPT Action in ChatGPT, enabling natural language queries via the ChatGPT interface.

## Features
- **Monetization Checker**: Estimates whether a YouTube channel or video is monetized based on YouTube Partner Program (YPP) thresholds (1,000 subscribers, 4,000 watch hours).
- **Analytics**: Fetches video stats (e.g., views, likes, comments) or channel stats (e.g., subscribers, total views, video count) using the YouTube Data API v3.
- **Authenticity Test**: Provides a basic check for content originality (e.g., based on video duration or tags).
- **Natural Language Prompt Support**: Processes user prompts like "Is this video monetized?" or "Get views" to return specific data.
- **GPT Action Integration**: Compatible with ChatGPT’s Custom GPT Actions for seamless natural language interaction.
- **Deployment**: Hosted on LeapCell for serverless, easy-to-manage deployment.

## Prerequisites
- **Python 3.8+**: Required to run the Flask application.
- **LeapCell Account**: For deploying the API (sign up at https://leapcell.io).
- **Google Cloud Account**: To obtain a YouTube Data API v3 key (https://console.cloud.google.com/).
- **ChatGPT Plus/Enterprise Account**: For creating and testing Custom GPT Actions (https://chat.openai.com).
- **Dependencies**:
  - `Flask==2.3.2`
  - `google-api-python-client==2.111.0`

## Installation

1. **Clone the Repository**:
   ```bash
   git clone 
   cd youtube-monetization-api
	2	Set Up Environment Variables:
	◦	Create a .env file in the project root (do not commit to git): YOUTUBE_API_KEY=your-youtube-api-key
	◦	
	◦	Obtain a YouTube API key:
	▪	Go to https://console.cloud.google.com/.
	▪	Create a project, enable the YouTube Data API v3, and generate an API key under “Credentials.”
	▪	Copy the key into .env.
	3	Install Dependencies: pip install -r requirements.txt
	4	
	5	Test Locally (optional): python main.py
	6	
	◦	The API will run at http://localhost:8080. Test with: curl -X POST http://localhost:8080/youtube-monetization \
	◦	-H "Content-Type: application/json" \
	◦	-d '{"video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "prompt": "Is this monetized?"}'
	◦	
Deployment on LeapCell
	1	Create a LeapCell Project:
	◦	Sign up at https://leapcell.io and log in.
	◦	Click “New Project” and select the “Python” template.
	2	Upload Files:
	◦	Upload main.py and requirements.txt to the LeapCell project.
	◦	Add the YOUTUBE_API_KEY in LeapCell’s environment variables (Settings > Environment Variables) instead of uploading .env.
	3	Deploy:
	◦	Click “Deploy” in the LeapCell dashboard. LeapCell will install dependencies and deploy the API.
	◦	Once deployed, note the public URL (e.g., https://your-app.leapcell.io).
	4	Test the Endpoint: curl -X POST https://your-app.leapcell.io/youtube-monetization \
	5	-H "Content-Type: application/json" \
	6	-d '{"video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "prompt": "Get views"}'
	7	
API Usage
Endpoint
	•	URL: POST /youtube-monetization
	•	Request Body (JSON): {
	•	  "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
	•	  "channel_id": "UCBR8-60-B28hp2BmDPdntcQ",
	•	  "prompt": "Is this monetized?"
	•	}
	•	
	◦	video_url: YouTube video URL (optional if channel_id is provided).
	◦	channel_id: YouTube channel ID or URL (optional if video_url is provided).
	◦	prompt: Optional natural language prompt (e.g., “Get subscribers,” “Is this original?”).
	◦	At least one of video_url or channel_id is required.
Example Requests and Responses
Video Monetization Check:
curl -X POST https://your-app.leapcell.io/youtube-monetization \
-H "Content-Type: application/json" \
-d '{"video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "prompt": "Is this monetized?"}'
Response:
{
  "is_monetized": true
}
Channel Subscribers:
curl -X POST https://your-app.leapcell.io/youtube-monetization \
-H "Content-Type: application/json" \
-d '{"channel_id": "UCBR8-60-B28hp2BmDPdntcQ", "prompt": "Get subscribers"}'
Response:
{
  "subscribers": "15000000"
}
Full Channel Stats (no prompt):
curl -X POST https://your-app.leapcell.io/youtube-monetization \
-H "Content-Type: application/json" \
-d '{"channel_id": "UCBR8-60-B28hp2BmDPdntcQ"}'
Response:
{
  "title": "YouTube Official Channel",
  "subscribers": "15000000",
  "video_count": "500",
  "total_views": "1000000000",
  "estimated_watch_hours": "83333333",
  "is_monetized": true
}
Integrating with ChatGPT as a Custom GPT Action
	1	Access GPT Builder:
	◦	Log in to https://chat.openai.com with a ChatGPT Plus or Enterprise account.
	◦	Click “Explore GPTs” > “Create a GPT.”
	2	Configure the GPT:
	◦	Set the name (e.g., “YouTube Monetization Checker”).
	◦	Add instructions: Use the YouTube Monetization API to check monetization status and fetch analytics for YouTube videos or channels based on user prompts. Accept a YouTube video URL or channel ID and process natural language queries like 'Is this monetized?' or 'Get subscribers.'
	◦	
	◦	Go to “Actions” > “Create new action.”
	3	Add OpenAPI Schema:
	◦	Copy the contents of openapi.yaml (included in the repository) or host it on a public URL (e.g., GitHub).
	◦	Paste the schema or URL into the Actions editor.
	◦	No authentication is required unless you add API key protection later.
	4	Test the Action:
	◦	In the GPT Builder’s playground, enter prompts like:
	▪	“Is https://www.youtube.com/watch?v=dQw4w9WgXcQ monetized?”
	▪	“Get subscribers for channel UCBR8-60-B28hp2BmDPdntcQ”
	◦	The GPT will call the /youtube-monetization endpoint and display results.
	5	Save and Share:
	◦	Click “Save” and choose visibility (e.g., “Only me” or “Public”).
	◦	Share the GPT link with others (requires ChatGPT Plus/Enterprise).
OpenAPI Schema
The openapi.yaml file defines the API’s structure for GPT Action integration. Host it publicly (e.g., on GitHub) or paste it directly into ChatGPT’s Action editor. Key details:
	•	Endpoint: /youtube-monetization
	•	Parameters: video_url, channel_id, prompt
	•	Responses: JSON with monetization status, analytics, or prompt-specific data.
Limitations
	•	Monetization Status: Estimated based on YPP thresholds (1,000 subscribers, 4,000 watch hours). YouTube’s API doesn’t expose monetization directly, so results are heuristic.
	•	Authenticity Test: Basic check based on video duration and tags (e.g., Shorts may be flagged as less original). ytlarge.com may use proprietary data for better accuracy.
	•	YouTube API Quotas: Free tier allows ~10,000 units/day (~100 queries). Monitor usage in Google Cloud Console.
	•	Prompt Processing: Supports basic prompts (e.g., “monetized,” “views”). For advanced NLP (e.g., summarization), integrate an LLM API like OpenAI.
	•	Security: The API is public. Add API key authentication for production use.
Extending the Project
	•	Add Transcripts: Integrate a YouTube Transcript API (e.g., via RapidAPI) for video content analysis.
	•	Advanced NLP: Use an LLM (e.g., OpenAI) for summarizing videos or processing complex prompts.
	•	Additional Tools: Implement ytlarge.com’s secondary features (e.g., thumbnail downloader, tag extractor) as new endpoints.
	•	Authentication: Add API key or OAuth for secure access.
Contributing
Contributions are welcome! Submit a pull request or open an issue for bugs, feature requests, or improvements.
License
This project is licensed under the MIT License. See LICENSE for details.
