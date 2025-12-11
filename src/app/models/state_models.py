from pydantic import BaseModel
from typing import Optional
from threading import Lock
import time


class SystemStats(BaseModel):
    cpu_temp: Optional[float] = None
    cpu_usage: Optional[float] = None
    ram_usage: Optional[float] = None
    disk_usage: Optional[float] = None


class RoverState(BaseModel):
    is_connected: bool = False
    is_driving: bool = False
    is_armed: bool = False
    camera_online: Optional[bool] = False
    mode: Optional[str] = None


class EnvironmentSensorsState(BaseModel):
    humidity: Optional[float] = None
    pressure: Optional[float] = None
    temperature: Optional[float] = None


# class CacheState(BaseModel):
#     user_data_fetched: Optional[bool] = None
#     last_update_timestamp: Optional[float] = None  # Using float for a Unix timestamp
#     rover_state: Optional[RoverState] = None
#     environment_sensors: Optional[EnvironmentSensorsState] = None
#     system_stats: Optional[SystemStats] = None


# Initialize the Cache State
# CACHE_LOCK = Lock()
# GLOBAL_CACHE_INSTANCE = CacheState(
#     user_data_fetched=False,
#     last_update_timestamp=None,
#     rover_state=RoverState(),
#     environment_sensors=EnvironmentSensorsState(),
#     system_stats=SystemStats(),
# )


# def update_user_data_cache(is_fetched: bool, cache_update: CacheState):
#     with CACHE_LOCK:
#         GLOBAL_CACHE_INSTANCE = cache_update
#         GLOBAL_CACHE_INSTANCE.user_data_fetched = is_fetched
#         GLOBAL_CACHE_INSTANCE.last_update_timestamp = time.time()


# def get_current_cache_state() -> CacheState:
#     with CACHE_LOCK:
#         return GLOBAL_CACHE_INSTANCE
