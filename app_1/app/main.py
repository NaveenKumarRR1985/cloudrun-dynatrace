from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .routers import health, api, web
import os

# Create FastAPI app
app = FastAPI(
    title="FastAPI OpenTelemetry Demo",
    description="A beautiful FastAPI application with OpenTelemetry auto-instrumentation",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Request counter middleware
@app.middleware("http")
async def count_every_request(request: Request, call_next):
    response = await call_next(request)
    from .routers import health
    health.request_count += 1
    return response

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(api.router, prefix="/api", tags=["API"])
app.include_router(web.router, tags=["Web UI"])

@app.on_event("startup")
async def startup_event():
    print("🚀 FastAPI application starting up!")
    print(f"📊 OTEL endpoint: {os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', 'Not configured')}")
    print("🎨 Beautiful UI available at http://localhost:8000")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
