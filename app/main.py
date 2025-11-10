from fastapi import FastAPI, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from jose import JWTError


from app.api.routes import (
    auth_routes,
    user_routes,
    chat_room_routes,
    message_routes,
    room_participant_routes,
    ws_routes,
)

from app.core.exceptions import (
    http_exception_handler,
    sqlalchemy_exception_handler,
    jwt_exception_handler,
    general_exception_handler,
)


app = FastAPI(
    title="Real-Time Chat API",
    description="A FastAPI-based real-time chat application with WebSocket support.",
    version="1.0.0"
)


app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(chat_room_routes.router)
app.include_router(message_routes.router)
app.include_router(room_participant_routes.router)
app.include_router(ws_routes.router)


app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(JWTError, jwt_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


@app.get("/")
async def root():
    return {"message": "Welcome to the Real-Time Chat Application!"}

