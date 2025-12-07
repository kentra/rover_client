from typing import Union

from fastapi import FastAPI
from app.routers import state
from app.routers import web_socket


app = FastAPI()
app.include_router(state.router)
app.include_router(web_socket.router)
