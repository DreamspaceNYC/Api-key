# YouTube Toolkit API Deployment

## Prerequisites
- Python 3.9+
- LeapCell account
- Google Cloud API key: 
## Setup
1. Install dependencies:
   ```bash
   pip install fastapi uvicorn google-api-python-client
   ```
2. Save `main.py` and `openapi.yaml` in a project folder.

## Deployment on LeapCell
1. Sign up/login at [LeapCell](https://leapcell.com).
2. Create a new project and upload the project folder.
3. Set environment variable:
   - Key: `API_KEY`
   - Value: `
4. Deploy the app. Note the generated endpoint URL (e.g., `https://your-leapcell-endpoint.com`).
5. Update `openapi.yaml` with your endpoint URL.

## Connect to GPT Action
1. Go to [chat.openai.com/create](https://chat.openai.com/create).
2. Create a new GPT and go to the "Configure" tab.
3. Add a new action, upload `openapi.yaml`.
4. Save and test with prompts like "Check monetization for dQw4w9WgXcQ".
