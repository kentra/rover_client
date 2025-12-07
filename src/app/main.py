from typing import Union

from fastapi import FastAPI
from app.routers import state


app = FastAPI()
app.include_router(state.router)


