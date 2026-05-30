# backend/middleware/logging.py

import time
from fastapi import Request


async def log_requests(request: Request, call_next):
    """
    Runs on every request automatically.
    Logs the method, path, status code and response time.

    Example log line:
    POST /ask → 200 (342ms)
    """
    start    = time.time()
    response = await call_next(request)
    elapsed  = round((time.time() - start) * 1000, 1)

    print(f"{request.method} {request.url.path} "
          f"→ {response.status_code} ({elapsed}ms)")

    return response