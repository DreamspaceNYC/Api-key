# ytlargeGPT

Backend service to analyze YouTube videos and return basic metadata and a
simulated monetization flag.

## Running locally

```bash
pip install -r requirements.txt
python main.py
```

POST a JSON payload containing a `url` field to `/analyze`.

Additional endpoints:
* `GET /` simple health check.
* `POST /ytlarge-info` accepts a JSON body with `url` and returns simulated video insights.
* OpenAPI specification is available in `openapi.yaml`.