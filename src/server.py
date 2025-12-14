import asyncio
import time
import uuid
from typing import List, Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import existing logic
from utils.logger import logger
from utils.docker_logs_extract import get_logs_since
from task_executor import run_agent
from task_extractor2 import task_extractor
from main import parse_docker_timestamp

app = FastAPI()

# Allow CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store connected clients
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting: {e}")

log_manager = ConnectionManager()
action_manager = ConnectionManager()

# State
pending_actions: Dict[str, Dict] = {}  # id -> {text, count, ...}
# We use a simple hash of the action text to detect duplicates or just exact string match
action_text_to_id: Dict[str, str] = {}

class ActionRequest(BaseModel):
    action_id: str

@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    await log_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text() # Keep connection alive
    except WebSocketDisconnect:
        log_manager.disconnect(websocket)

@app.websocket("/ws/actions")
async def websocket_actions(websocket: WebSocket):
    await action_manager.connect(websocket)
    # Send current state on connect
    await websocket.send_json(list(pending_actions.values()))
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        action_manager.disconnect(websocket)

@app.post("/api/actions/{action_id}/approve")
async def approve_action(action_id: str, background_tasks: BackgroundTasks):
    if action_id in pending_actions:
        action = pending_actions.pop(action_id)
        # Execute in background
        background_tasks.add_task(run_agent, action["text"])
        
        # Remove from mapping
        # Find key by value (inefficient but safe for small dicts)
        for k, v in list(action_text_to_id.items()):
            if v == action_id:
                del action_text_to_id[k]
                break
        
        # Broadcast update
        await action_manager.broadcast(list(pending_actions.values()))
        return {"status": "approved", "action": action["text"]}
    return {"status": "not_found"}

@app.post("/api/actions/{action_id}/reject")
async def reject_action(action_id: str):
    if action_id in pending_actions:
        action = pending_actions.pop(action_id)
        
        for k, v in list(action_text_to_id.items()):
            if v == action_id:
                del action_text_to_id[k]
                break
                
        await action_manager.broadcast(list(pending_actions.values()))
        return {"status": "rejected"}
    return {"status": "not_found"}


# Background Log Worker
async def log_worker():
    last_ts = time.time()
    print(f"Server log monitor started at {last_ts}")
    
    while True:
        await asyncio.sleep(2)
        try:
            # We run the blocking docker call in a thread if needed, 
            # but for now let's hope it's fast enough or use asyncio.to_thread
            logs_bytes = await asyncio.to_thread(get_logs_since, "book-service", last_ts)
            
            if not logs_bytes:
                continue
                
            logs_decoded = logs_bytes.decode("utf-8", errors="replace").strip()
            if not logs_decoded:
                continue
                
            lines = logs_decoded.splitlines()
            batch_content = []
            max_ts_in_batch = last_ts

            for line in lines:
                parts = line.split(" ", 1)
                if len(parts) < 2:
                    continue
                
                ts_str, content = parts[0], parts[1]
                
                # Use existing parser
                current_log_ts = parse_docker_timestamp(ts_str)
                
                if current_log_ts > last_ts:
                    batch_content.append(content)
                    if current_log_ts > max_ts_in_batch:
                        max_ts_in_batch = current_log_ts
            
            last_ts = max_ts_in_batch
            
            if batch_content:
                log_string = "\n".join(batch_content)
                # Broadcast logs
                await log_manager.broadcast({"logs": log_string})
                
                # Run Task Extractor
                task = await asyncio.to_thread(task_extractor, log_string)
                if task:
                    print(f"Task found: {task}")
                    # Update Actions
                    if task in action_text_to_id:
                        # Existing action, increment count
                        existing_id = action_text_to_id[task]
                        pending_actions[existing_id]["count"] += 1
                    else:
                        # New action
                        new_id = str(uuid.uuid4())
                        action_text_to_id[task] = new_id
                        pending_actions[new_id] = {
                            "id": new_id,
                            "text": task,
                            "count": 1,
                            "timestamp": time.time()
                        }
                    
                    # Broadcast updated actions
                    await action_manager.broadcast(list(pending_actions.values()))

        except Exception as e:
            print(f"Error in log worker: {e}")

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(log_worker())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
