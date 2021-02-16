from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.server.routes.auth import router as AuthRouter
from src.server.routes.student import router as StudentRouter
from src.server.core.exceptions.application import ApplicationException

app = FastAPI()

app.include_router(AuthRouter, tags=["Authentication"], prefix="/auth")
app.include_router(StudentRouter, tags=["Student"], prefix="/students")


@app.exception_handler(ApplicationException)
async def custom_exception_handler(request: Request, exc: ApplicationException):
    response = {"error": {"code": exc.code, "tip": exc.tip, "message": exc.message}}
    return JSONResponse(status_code=exc.code, content=response)


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to this fantastic app!"}