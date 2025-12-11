from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import state
from app.routers import web_socket
from app.routers import movement
from app.hardware.env_sensors import EnvironmentSensors
from app.shared import hub, cfg


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting up... Connecting to Rover...")
    try:
        await hub.connect()
    except Exception as e:
        print(f"⚠️ Failed to connect on startup: {e}")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down... Disconnecting...")
    await hub.disconnect()


app = FastAPI(lifespan=lifespan)

# Mount static files
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static"), html=True), name="static")

env_sensors = EnvironmentSensors(bus_number=cfg.BME280_I2C_BUS)


from fastapi.responses import HTMLResponse
import random

app.include_router(state.router)
app.include_router(web_socket.router)
app.include_router(movement.router)


@app.get("/remote", response_class=HTMLResponse)
async def remote_control():
    path = BASE_DIR / "models" / "remote_control.html"
    with open(path, "r") as f:
        return f.read()

@app.get("/distance")
async def get_distance():
    # Placeholder for distance sensor
    return f"{random.uniform(10.0, 50.0):.2f}"

@app.get("/matrix")
async def toggle_matrix():
    print("Matrix toggled")
    return {"status": "ok"}

@app.get("/buzzer")
async def toggle_buzzer():
    print("Buzzer toggled")
    return {"status": "ok"}


