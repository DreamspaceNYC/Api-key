# YouTube Video Analysis API

A FastAPI application that mimics ytlarge.com, fetching YouTube video metadata (title, views, likes, comments, etc.) from a video URL. Deployed on LeapCell and integrated with ChatGPT Custom GPT Action.

## Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/youtube-analysis-api.git
   cd youtube-analysis-api
   ```
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Set Environment Variables**: Create a `.env` file with:
   ```
   YOUTUBE_API_KEY=your_youtube_api_key_here
   ```
   Get your API key from Google Cloud Console.
4. **Run Locally**:
   ```bash
   uvicorn main:app --reload
   ```

## Deploy to LeapCell

1. Connect this repo to LeapCell.
2. Set `YOUTUBE_API_KEY` in LeapCell’s environment variables.
3. Deploy using LeapCell’s GitHub integration.

## API Endpoint

- **POST `/video-stats`**: Accepts a JSON body with `video_url` and returns video metadata. Example:
  ```bash
  curl -X POST "https://your-leapcell-app.leapcell.io/video-stats" \
       -H "Content-Type: application/json" \
       -d '{"video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
  ```

## GPT Action

- Import the OpenAPI schema from `https://your-leapcell-app.leapcell.io/openapi.json` in ChatGPT’s GPT builder.

	•	Advanced NLP: Use an LLM (e.g., OpenAI) for summarizing videos or processing complex prompts.
	•	Additional Tools: Implement ytlarge.com’s secondary features (e.g., thumbnail downloader, tag extractor) as new endpoints.
	•	Authentication: Add API key or OAuth for secure access.
Contributing
Contributions are welcome! Submit a pull request or open an issue for bugs, feature requests, or improvements.
License
This project is licensed under the MIT License. See LICENSE for details.
