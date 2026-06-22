import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import converter

# Instantiate the primary FastAPI engine
app = FastAPI(
    title="Flash Converter API Core",
    description="Minimalist high-performance asynchronous media resolution & transcoding pipelines.",
    version="3.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS Policy - Explicitly expose the Content-Disposition header so JavaScript can read filenames
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to specific production domain scopes in enterprise deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"] # MUST BE EXPOSED so the frontend can read backend filenames!
)

# Bind the converter route endpoints
app.include_router(converter.router, prefix="/api")

@app.get("/api/health", tags=["System Utility"])
async def system_health_status():
    """
    Standard heartbeat monitoring.
    Uses our classic brand flavor: 80% professional, 20% clever.
    """
    return {
        "status": "online",
        "message": "Servers are operational. The hamsters are currently hydrated.",
        "api_layer": "FastAPI",
        "transcoding_pipeline": "FFmpeg Ready"
    }

if __name__ == "__main__":
    # Launch Uvicorn local development server
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)