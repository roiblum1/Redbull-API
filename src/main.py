"""Main FastAPI application for MCE Cluster Generator."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from utils.logging_config import setup_logging
from utils.exceptions import MCEGeneratorError
from api.routers import clusters
from api.models.responses import HealthResponse, ErrorResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    setup_logging(
        level=settings.LOG_LEVEL,
        log_file=settings.LOG_FILE,
        enable_rich=not settings.DEBUG  # Disable rich in production
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"GitOps Repository: {settings.GITOPS_REPO_URL}")
    logger.info(f"Access Mode: {settings.REPO_ACCESS_MODE}")
    
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

# Include routers
app.include_router(clusters.router, prefix="/api/v1")


@app.get("/", response_model=HealthResponse, tags=["health"])
async def root():
    """Root endpoint - health check."""
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION
    )


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION
    )


@app.exception_handler(MCEGeneratorError)
async def mce_generator_exception_handler(request, exc: MCEGeneratorError):
    """Handle MCE Generator specific errors."""
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            error=exc.message,
            details=exc.details
        ).model_dump()
    )


@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(
            error="Resource not found",
            details={"path": str(request.url.path)}
        ).model_dump()
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )