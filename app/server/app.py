from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


from server.routes.student import router as StudentRouter
from server.routes.auth import router as AuthRouter
from server.core.exceptions.application import ApplicationException

app = FastAPI()

app.include_router(StudentRouter, tags=["Student"], prefix="/students")
app.include_router(AuthRouter, tags=["Authentication"], prefix="/auth")


@app.exception_handler(ApplicationException)
async def custom_exception_handler(request: Request, exc: ApplicationException):
    response = {
        "error": {"code": exc.code, "reason": exc.reason, "message": exc.message}
    }
    return JSONResponse(status_code=exc.code, content=response)


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to this fantastic app!"}