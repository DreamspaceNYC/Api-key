# ytlargeGPT

Backend service to analyze YouTube videos and return basic metadata and a
simulated monetization flag.

## Running locally

```bash
pip install -r requirements.txt
python main.py
```

POST a JSON payload containing a `url` field to `/analyze`.

OpenAPI specification is available in `openapi.yaml`.
