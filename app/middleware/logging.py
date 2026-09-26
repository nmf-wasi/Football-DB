import time
import logging
from fastapi import Request

logger = logging.getLogger(__name__)


async def logging_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    durantion = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code} - {durantion:0.3f}s"
    )
    
    return response
