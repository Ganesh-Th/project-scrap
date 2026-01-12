"""WebSocket connection manager with Redis pub/sub."""
import json
import asyncio
from typing import Dict, Set
from fastapi import WebSocket
from app.core.redis_store import get_redis_store
from app.logging_config import get_logger
from app.models.responses import TaskStatus, ProgressUpdate


logger = get_logger(__name__)


class ConnectionManager:
    """Manages WebSocket connections with Redis pub/sub for progress updates."""
    
    def __init__(self):
        # Map of task_id -> set of WebSocket connections
        self._connections: Dict[str, Set[WebSocket]] = {}
        # Map of task_id -> asyncio task for pub/sub listener
        self._listeners: Dict[str, asyncio.Task] = {}
    
    async def connect(self, websocket: WebSocket, task_id: str) -> None:
        """Accept WebSocket connection and subscribe to task updates."""
        await websocket.accept()
        
        if task_id not in self._connections:
            self._connections[task_id] = set()
        self._connections[task_id].add(websocket)
        
        logger.info(f"WebSocket connected for task: {task_id}")
        
        # Send current task state immediately
        await self._send_current_state(websocket, task_id)
        
        # Start listener if not already running
        if task_id not in self._listeners or self._listeners[task_id].done():
            self._listeners[task_id] = asyncio.create_task(
                self._listen_for_updates(task_id)
            )
    
    async def disconnect(self, websocket: WebSocket, task_id: str) -> None:
        """Remove WebSocket connection."""
        if task_id in self._connections:
            self._connections[task_id].discard(websocket)
            
            # Clean up listener if no more connections
            if not self._connections[task_id]:
                del self._connections[task_id]
                
                if task_id in self._listeners:
                    self._listeners[task_id].cancel()
                    del self._listeners[task_id]
        
        logger.info(f"WebSocket disconnected for task: {task_id}")
    
    async def _send_current_state(self, websocket: WebSocket, task_id: str) -> None:
        """Send current task state when client connects."""
        try:
            store = await get_redis_store()
            task_data = await store.get_task(task_id)
            
            if task_data:
                update = ProgressUpdate(
                    task_id=task_id,
                    status=TaskStatus(task_data.get("status", "pending")),
                    progress=int(task_data.get("progress", 0)),
                    total=100,
                    message=task_data.get("message", "")
                )
                await websocket.send_json(update.model_dump())
            else:
                await websocket.send_json({
                    "task_id": task_id,
                    "error": "Task not found"
                })
        except Exception as e:
            logger.error(f"Error sending current state: {e}")
            await websocket.send_json({
                "task_id": task_id,
                "error": str(e)
            })
    
    async def _listen_for_updates(self, task_id: str) -> None:
        """Listen for Redis pub/sub messages and broadcast to WebSockets."""
        try:
            store = await get_redis_store()
            
            async with store.subscribe_to_progress(task_id) as pubsub:
                while task_id in self._connections and self._connections[task_id]:
                    try:
                        message = await asyncio.wait_for(
                            pubsub.get_message(ignore_subscribe_messages=True),
                            timeout=1.0
                        )
                        
                        if message and message.get("type") == "message":
                            data = message.get("data")
                            if isinstance(data, str):
                                await self._broadcast(task_id, json.loads(data))
                            
                    except asyncio.TimeoutError:
                        # Check if task is completed
                        task_data = await store.get_task(task_id)
                        if task_data:
                            status = task_data.get("status")
                            if status in (TaskStatus.COMPLETED.value, TaskStatus.FAILED.value):
                                # Send final state and stop listening
                                await self._broadcast_final_state(task_id, task_data)
                                break
                    except asyncio.CancelledError:
                        break
                    except Exception as e:
                        logger.error(f"Error in pub/sub listener: {e}")
                        await asyncio.sleep(1)
                        
        except Exception as e:
            logger.error(f"Listener error for task {task_id}: {e}")
    
    async def _broadcast(self, task_id: str, data: dict) -> None:
        """Broadcast message to all connections for a task."""
        if task_id not in self._connections:
            return
        
        disconnected = set()
        
        for websocket in self._connections[task_id]:
            try:
                await websocket.send_json(data)
            except Exception:
                disconnected.add(websocket)
        
        # Clean up disconnected sockets
        for websocket in disconnected:
            self._connections[task_id].discard(websocket)
    
    async def _broadcast_final_state(self, task_id: str, task_data: dict) -> None:
        """Broadcast final task state with result."""
        if task_id not in self._connections:
            return
        
        status = TaskStatus(task_data.get("status"))
        
        message = {
            "task_id": task_id,
            "status": status.value,
            "progress": 100 if status == TaskStatus.COMPLETED else 0,
            "total": 100,
            "message": "Task completed" if status == TaskStatus.COMPLETED else task_data.get("error", "Task failed"),
            "result_available": task_data.get("result") is not None,
            "error": task_data.get("error")
        }
        
        await self._broadcast(task_id, message)


# Singleton instance
_manager: ConnectionManager | None = None


def get_connection_manager() -> ConnectionManager:
    """Get connection manager singleton."""
    global _manager
    if _manager is None:
        _manager = ConnectionManager()
    return _manager
