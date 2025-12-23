"""Main FastAPI application for MCE Cluster Generator."""

from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from config.settings import settings
from utils.logging import setup_logging, get_logger
from utils.exceptions import MCEGeneratorError
from api.routers import clusters
from api.middleware.logging_middleware import RequestLoggingMiddleware
from models.responses import HealthResponse, ErrorResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    setup_logging(
        level=settings.LOG_LEVEL,
        log_file=settings.LOG_FILE,
        enable_rich=not settings.DEBUG
    )

    logger = get_logger(__name__)
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Default OCP Version: {settings.DEFAULT_OCP_VERSION}")
    logger.info(f"Default DNS Domain: {settings.DEFAULT_DNS_DOMAIN}")
    logger.info(f"Supported Vendors: {', '.join(settings.SUPPORTED_VENDORS)}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down MCE Cluster Generator API")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request/response logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Include API routers
app.include_router(clusters.router, prefix="/api/v1")

# Mount static files for UI
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


@app.get("/", response_class=HTMLResponse, tags=["ui"])
async def serve_ui():
    """Serve the main UI page."""
    index_path = Path(__file__).parent / "static" / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    
    # Fallback if static files don't exist yet
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>MCE Cluster Generator</title>
        <style>
            body { font-family: system-ui; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background: #1a1a2e; color: #eee; }
            .container { text-align: center; }
            a { color: #4da6ff; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 MCE Cluster Generator</h1>
            <p>UI is loading... If this persists, check static files.</p>
            <p><a href="/docs">API Documentation</a></p>
        </div>
    </body>
    </html>
    """)


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION
    )


@app.get("/api/health", response_model=HealthResponse, tags=["health"])
async def api_health_check():
    """API health check endpoint."""
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION
    )


@app.exception_handler(MCEGeneratorError)
async def mce_generator_exception_handler(request: Request, exc: MCEGeneratorError):
    """Handle MCE Generator specific errors."""
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            error=exc.message,
            details=exc.details
        ).model_dump()
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors."""
    # Check if it's an API request
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=404,
            content=ErrorResponse(
                error="Resource not found",
                details={"path": str(request.url.path)}
            ).model_dump()
        )
    
    # For non-API requests, serve the UI (SPA fallback)
    index_path = Path(__file__).parent / "static" / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(
            error="Resource not found",
            details={"path": str(request.url.path)}
        ).model_dump()
    )


if __name__ == "__main__":
    import uvicorn

    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"Server: http://{settings.HOST}:{settings.PORT}")
    print(f"UI: http://{settings.HOST}:{settings.PORT}/")
    print(f"API Documentation: http://{settings.HOST}:{settings.PORT}/docs")

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
