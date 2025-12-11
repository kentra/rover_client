from fastapi import WebSocket, APIRouter, WebSocketDisconnect
import json
from app.shared import hub

router = APIRouter(
    tags=["websocket"],
)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data_text = await websocket.receive_text()
            try:
                data = json.loads(data_text)
                # Check for direct track control commands
                if "left" in data and "right" in data:
                    left = int(data["left"])
                    right = int(data["right"])
                    await hub.drive_tracks(left, right)
            except json.JSONDecodeError:
                print(f"⚠️ Invalid JSON received: {data_text}")
            except Exception as e:
                print(f"⚠️ Error processing command: {e}")
                
    except WebSocketDisconnect:
        print("🔌 WebSocket disconnected")
        await hub.drive_tracks(0, 0) # Safety stop

