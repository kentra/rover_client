from fastapi import APIRouter
from app.shared import hub

router = APIRouter(
    prefix="/move",
    tags=["movement"],
)


@router.get("/{direction}")
async def move(direction: str):
    """
    Handle movement commands from remote_control.html
    Directions: forward, back, left, right, stop, crab_left, crab_right
    """
    speed = 50  # Default speed
    
    if direction == "forward":
        await hub.drive_tracks(speed, speed)
    elif direction == "back":
        await hub.drive_tracks(-speed, -speed)
    elif direction == "left":
        await hub.drive_tracks(-speed, speed)
    elif direction == "right":
        await hub.drive_tracks(speed, -speed)
    elif direction == "stop":
        await hub.drive_tracks(0, 0)
    elif direction == "crab_left":
         # Assuming crab means pivot or just track diff? 
         # With 2 tracks, crab isn't really possible unless omni-wheels.
         # Assuming spin left for now or simplified turn.
         await hub.drive_tracks(0, speed)
    elif direction == "crab_right":
         await hub.drive_tracks(speed, 0)
    else:
        return {"status": "unknown command"}
        
    return {"status": "ok", "direction": direction}

