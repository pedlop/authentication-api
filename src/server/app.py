from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from src.server.routes.auth import router as AuthRouter
from src.server.core.exceptions.application import ApplicationException

app = FastAPI()


origins = [
    "http://localhost",
    "http://localhost:4201",
    "https://cash.pedlop.com",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=["pedlop.com", "*.pedlop.com", "localhost"]
)

app.include_router(AuthRouter, tags=["Authentication"], prefix="/auth")


@app.exception_handler(ApplicationException)
async def custom_exception_handler(request: Request, exc: ApplicationException):
    response = {"error": {"code": exc.code, "tip": exc.tip, "message": exc.message}}
    return JSONResponse(status_code=exc.code, content=response)


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to this fantastic app!"}