from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.audit import audit_event
from app.core.security_controls import enforce_api_rate_limit


class SecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/api"):
            enforce_api_rate_limit(request)

        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        if request.url.path.startswith("/api/auth") or request.url.path == "/api/login":
            response.headers["Cache-Control"] = "no-store"
            response.headers["Pragma"] = "no-cache"

        if response.status_code == 401:
            audit_event("unauthorized", path=request.url.path, method=request.method)
        elif response.status_code == 403:
            audit_event("forbidden", path=request.url.path, method=request.method)

        return response
