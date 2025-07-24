import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from typing import Callable

logger = logging.getLogger(__name__)


async def error_handler_middleware(request: Request, call_next: Callable):
    """Global error handler middleware."""
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Unhandled error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "type": type(e).__name__,
                "message": str(e)
            }
        )