from fastapi import FastAPI, Request, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

security = HTTPBasic()

class BasicAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, username: str, password: str):
        super().__init__(app)
        self.username = username
        self.password = password

    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/docs") or request.url.path.startswith("/redoc"):
            credentials: HTTPBasicCredentials = await security(request)
            if not (credentials.username == self.username and credentials.password == self.password):
                return Response("Unauthorized", status_code=401, headers={"WWW-Authenticate": "Basic"})
        response = await call_next(request)
        return response
