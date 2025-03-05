from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from app.core.config import settings
from app.core.logging import setup_logging

# Set up logging only once at module level
setup_logging()

# Create FastAPI app
app = FastAPI(
    title="Brand Safety Analysis API",
    description="API for classifying images into brand safety categories",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers after app creation to avoid circular imports
from app.api.endpoints import classification, health

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(classification.router, prefix="/api/v1", tags=["classification"])

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for the FastAPI application.
    
    This handler catches all unhandled exceptions and returns a standardized error response.
    
    Args:
        request: FastAPI request
        exc: Exception that was raised
        
    Returns:
        JSONResponse with error details
    """
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "message": "An unexpected error occurred",
                "code": 500
            }
        }
    )

@app.on_event("startup")
async def startup_event():
    """
    Startup event handler.
    
    This function is called when the FastAPI application starts up.
    It logs the startup and performs any necessary initialization.
    """
    logger.info(f"[API] Starting Brand Safety Analysis API on {settings.API_HOST}:{settings.API_PORT}")
    logger.info(f"[API] OpenAI Model: {settings.OPENAI_MODEL}")
    logger.info(f"[API] Data Directory: {settings.DATA_DIR}")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event handler.
    
    This function is called when the FastAPI application shuts down.
    It logs the shutdown and performs any necessary cleanup.
    """
    logger.info("[API] Shutting down Brand Safety Analysis API")

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
    )