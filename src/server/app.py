from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from src.server.routes.auth import router as AuthRouter
from src.server.core.exceptions.application import ApplicationException

app = FastAPI()

app.include_router(AuthRouter, tags=["Authentication"], prefix="/auth")

origins = ["http://localhost", "http://localhost:4201"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex="https://.*\.pedlop\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ApplicationException)
async def custom_exception_handler(request: Request, exc: ApplicationException):
    response = {"error": {"code": exc.code, "tip": exc.tip, "message": exc.message}}
    return JSONResponse(status_code=exc.code, content=response)


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to this fantastic app!"}