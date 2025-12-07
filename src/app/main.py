from typing import Union

from fastapi import FastAPI
from app.routers import state
from app.routers import web_socket
from app.routers import movement
from app.models import state_models


GLOBAL_CACHE_INSTANCE = state_models.CacheState(
    user_data_fetched=False, last_update_timestamp=None
)

app = FastAPI()
app.include_router(state.router)
app.include_router(web_socket.router)
app.include_router(movement.router)
