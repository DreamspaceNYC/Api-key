
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import json
from datetime import datetime

app = FastAPI(
    title="YTLarge API Wrapper",
    description="A web API wrapper service that connects to ytlarge and provides structured endpoints for OpenAI Custom GPT Actions",
    version="1.0.0",
    openapi_tags=[
        {"name": "videos", "description": "YouTube video operations"},
        {"name": "search", "description": "Search operations"},
        {"name": "transcripts", "description": "Video transcript operations"},
        {"name": "metadata", "description": "Video metadata operations"}
    ]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base ytlarge API configuration
YTLARGE_BASE_URL = "https://ytlarge.com/api"

class APIResponse:
    @staticmethod
    def success(data: Any, message: str = "Success") -> Dict[str, Any]:
        return {
            "success": True,
            "message": message,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def error(message: str, error_code: str = "API_ERROR") -> Dict[str, Any]:
        return {
            "success": False,
            "message": message,
            "error_code": error_code,
            "timestamp": datetime.utcnow().isoformat()
        }

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>YTLarge API Wrapper</title>
        <style>
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background-color: #F7F7F8;
                color: #202123;
                margin: 0;
                padding: 40px 20px;
                line-height: 1.6;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            .header {
                text-align: center;
                margin-bottom: 50px;
            }
            .logo {
                font-size: 2.5rem;
                font-weight: 700;
                color: #10A37F;
                margin-bottom: 10px;
            }
            .subtitle {
                font-size: 1.2rem;
                color: #666;
                margin-bottom: 30px;
            }
            .endpoints {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            }
            .endpoint-card {
                background: white;
                border-radius: 12px;
                padding: 25px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                border-left: 4px solid #10A37F;
            }
            .endpoint-card h3 {
                margin: 0 0 10px 0;
                color: #202123;
                font-size: 1.1rem;
            }
            .endpoint-card .method {
                display: inline-block;
                padding: 4px 8px;
                border-radius: 6px;
                font-size: 0.8rem;
                font-weight: 600;
                margin-bottom: 10px;
            }
            .get { background: #059669; color: white; }
            .post { background: #FF0000; color: white; }
            .endpoint-card .path {
                font-family: 'JetBrains Mono', monospace;
                background: #1F2937;
                color: #F9FAFB;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 0.9rem;
                margin: 10px 0;
            }
            .description {
                color: #666;
                font-size: 0.9rem;
            }
            .features {
                background: white;
                border-radius: 12px;
                padding: 30px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                margin-bottom: 30px;
            }
            .features h2 {
                color: #202123;
                margin-bottom: 20px;
                border-bottom: 2px solid #10A37F;
                padding-bottom: 10px;
            }
            .feature-list {
                list-style: none;
                padding: 0;
            }
            .feature-list li {
                padding: 8px 0;
                padding-left: 25px;
                position: relative;
            }
            .feature-list li::before {
                content: "â";
                position: absolute;
                left: 0;
                color: #10A37F;
                font-weight: bold;
            }
            .docs-link {
                text-align: center;
                margin-top: 30px;
            }
            .docs-link a {
                display: inline-block;
                background: #10A37F;
                color: white;
                padding: 12px 30px;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 600;
                transition: background 0.3s;
            }
            .docs-link a:hover {
                background: #059669;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">YTLarge API Wrapper</div>
                <div class="subtitle">Structured YouTube content access for OpenAI Custom GPT Actions</div>
            </div>

            <div class="features">
                <h2>Core Features</h2>
                <ul class="feature-list">
                    <li>API endpoints that interface with ytlarge.com services</li>
                    <li>JSON response formatting compatible with OpenAI Custom GPT Actions</li>
                    <li>Authentication and request handling for ytlarge.com integration</li>
                    <li>OpenAPI specification document for GPT Action configuration</li>
                </ul>
            </div>

            <div class="endpoints">
                <div class="endpoint-card">
                    <h3>Search Videos</h3>
                    <span class="method get">GET</span>
                    <div class="path">/api/search</div>
                    <div class="description">Search for YouTube videos with query parameters</div>
                </div>
                
                <div class="endpoint-card">
                    <h3>Get Video Info</h3>
                    <span class="method get">GET</span>
                    <div class="path">/api/video/{video_id}</div>
                    <div class="description">Retrieve detailed information about a specific video</div>
                </div>
                
                <div class="endpoint-card">
                    <h3>Get Transcript</h3>
                    <span class="method get">GET</span>
                    <div class="path">/api/video/{video_id}/transcript</div>
                    <div class="description">Fetch video transcript/captions</div>
                </div>
                
                <div class="endpoint-card">
                    <h3>Video Metadata</h3>
                    <span class="method get">GET</span>
                    <div class="path">/api/video/{video_id}/metadata</div>
                    <div class="description">Get comprehensive video metadata</div>
                </div>
            </div>

            <div class="docs-link">
                <a href="/docs">View Interactive API Documentation</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/api/search", tags=["search"])
async def search_videos(
    q: str = Query(..., description="Search query"),
    max_results: int = Query(10, description="Maximum number of results", ge=1, le=50),
    order: str = Query("relevance", description="Sort order: relevance, date, rating, viewCount")
):
    """
    Search for YouTube videos using ytlarge API.
    
    This endpoint searches for videos based on the provided query and returns
    structured results compatible with OpenAI Custom GPT Actions.
    """
    try:
        async with httpx.AsyncClient() as client:
            # Simulate ytlarge API call (replace with actual endpoint)
            response = await client.get(
                f"{YTLARGE_BASE_URL}/search",
                params={
                    "q": q,
                    "maxResults": max_results,
                    "order": order
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return APIResponse.success(
                    data={
                        "query": q,
                        "results": data.get("items", []),
                        "total_results": len(data.get("items", [])),
                        "order": order
                    },
                    message=f"Found {len(data.get('items', []))} videos for query: {q}"
                )
            else:
                raise HTTPException(status_code=response.status_code, detail="YTLarge API error")
                
    except httpx.TimeoutException:
        raise HTTPException(status_code=408, detail="Request timeout")
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=APIResponse.error(f"Search failed: {str(e)}", "SEARCH_ERROR")
        )

@app.get("/api/video/{video_id}", tags=["videos"])
async def get_video_info(
    video_id: str = Path(..., description="YouTube video ID")
):
    """
    Get detailed information about a specific YouTube video.
    
    Returns comprehensive video data including title, description, duration,
    view count, and other metadata.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{YTLARGE_BASE_URL}/video/{video_id}",
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return APIResponse.success(
                    data=data,
                    message=f"Retrieved video information for {video_id}"
                )
            elif response.status_code == 404:
                raise HTTPException(status_code=404, detail="Video not found")
            else:
                raise HTTPException(status_code=response.status_code, detail="YTLarge API error")
                
    except httpx.TimeoutException:
        raise HTTPException(status_code=408, detail="Request timeout")
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=APIResponse.error(f"Failed to get video info: {str(e)}", "VIDEO_INFO_ERROR")
        )

@app.get("/api/video/{video_id}/transcript", tags=["transcripts"])
async def get_video_transcript(
    video_id: str = Path(..., description="YouTube video ID"),
    lang: Optional[str] = Query("en", description="Language code for transcript")
):
    """
    Get the transcript/captions for a YouTube video.
    
    Returns the full transcript text with timestamps if available.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{YTLARGE_BASE_URL}/video/{video_id}/transcript",
                params={"lang": lang} if lang else {},
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return APIResponse.success(
                    data={
                        "video_id": video_id,
                        "language": lang,
                        "transcript": data.get("transcript", ""),
                        "segments": data.get("segments", [])
                    },
                    message=f"Retrieved transcript for video {video_id}"
                )
            elif response.status_code == 404:
                raise HTTPException(status_code=404, detail="Transcript not available")
            else:
                raise HTTPException(status_code=response.status_code, detail="YTLarge API error")
                
    except httpx.TimeoutException:
        raise HTTPException(status_code=408, detail="Request timeout")
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=APIResponse.error(f"Failed to get transcript: {str(e)}", "TRANSCRIPT_ERROR")
        )

@app.get("/api/video/{video_id}/metadata", tags=["metadata"])
async def get_video_metadata(
    video_id: str = Path(..., description="YouTube video ID")
):
    """
    Get comprehensive metadata for a YouTube video.
    
    Returns detailed metadata including title, description, tags, duration,
    view count, like count, upload date, and channel information.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{YTLARGE_BASE_URL}/video/{video_id}/metadata",
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return APIResponse.success(
                    data=data,
                    message=f"Retrieved metadata for video {video_id}"
                )
            elif response.status_code == 404:
                raise HTTPException(status_code=404, detail="Video not found")
            else:
                raise HTTPException(status_code=response.status_code, detail="YTLarge API error")
                
    except httpx.TimeoutException:
        raise HTTPException(status_code=408, detail="Request timeout")
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=APIResponse.error(f"Failed to get metadata: {str(e)}", "METADATA_ERROR")
        )

@app.get("/openapi.json")
async def get_openapi():
    """
    Custom OpenAPI specification optimized for OpenAI Custom GPT Actions.
    """
    return app.openapi()

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return APIResponse.success(
        data={"status": "healthy", "service": "ytlarge-api-wrapper"},
        message="Service is running"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
