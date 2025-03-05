from fastapi import APIRouter
from loguru import logger
import platform
import psutil
import time

from app.core.config import settings
from app.utils.api_utils import format_success_response

router = APIRouter()

def get_system_info():
    """
    Get system information.
    
    This function collects information about the system, such as CPU usage,
    memory usage, and disk usage.
    
    Returns:
        Dictionary with system information
    """
    try:
        return {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent,
            "python_version": platform.python_version(),
            "platform": platform.platform()
        }
    except Exception as e:
        logger.error(f"Error getting system info: {str(e)}")
        return {}

@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    This endpoint returns the health status of the API, including system information
    and configuration settings.
    
    Returns:
        Health status
    """
    logger.info("Health check requested")
    
    # Get system information
    system_info = get_system_info()
    
    # Create health status
    health_status = {
        "status": "ok",
        "timestamp": time.time(),
        "system_info": system_info,
        "config": {
            "api_host": settings.API_HOST,
            "api_port": settings.API_PORT,
            "openai_model": settings.OPENAI_MODEL,
            "data_dir": settings.DATA_DIR,
            "log_level": settings.LOG_LEVEL
        }
    }
    
    return format_success_response(health_status)