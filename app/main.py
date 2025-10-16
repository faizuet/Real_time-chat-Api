from fastapi import FastAPI, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from jose import JWTError

from app.api.routes import auth
from app.core.exceptions import (
    http_exception_handler,
    sqlalchemy_exception_handler,
    jwt_exception_handler,
    general_exception_handler,
)


app = FastAPI(title="Real-Time Chat API")


app.include_router(auth.router)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(JWTError, jwt_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

@app.get("/")
async def root():
    return {"message": "Welcome to Real-Time Chat Application!"}

