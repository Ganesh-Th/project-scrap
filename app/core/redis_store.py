"""Redis task store for persistent task management."""
import json
from typing import Optional, Dict, Any
from datetime import datetime
import redis.asyncio as redis
from contextlib import asynccontextmanager

from app.config import get_settings
from app.logging_config import get_logger
from app.models.responses import TaskStatus, ProgressUpdate


logger = get_logger(__name__)
settings = get_settings()

# TTL for task data (24 hours)
TASK_TTL_SECONDS = 86400


class RedisTaskStore:
    """Async Redis client for task storage and pub/sub."""
    
    _instance: Optional["RedisTaskStore"] = None
    
    def __init__(self):
        self._pool: Optional[redis.ConnectionPool] = None
        self._client: Optional[redis.Redis] = None
        self._pubsub_client: Optional[redis.Redis] = None
    
    @classmethod
    async def get_instance(cls) -> "RedisTaskStore":
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
            await cls._instance.connect()
        return cls._instance
    
    async def connect(self) -> None:
        """Initialize Redis connection pool."""
        try:
            self._pool = redis.ConnectionPool.from_url(
                settings.REDIS_URL,
                max_connections=10,
                decode_responses=True
            )
            self._client = redis.Redis(connection_pool=self._pool)
            self._pubsub_client = redis.Redis(connection_pool=self._pool)
            
            # Test connection
            await self._client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close Redis connections."""
        if self._client:
            await self._client.aclose()
        if self._pubsub_client:
            await self._pubsub_client.aclose()
        if self._pool:
            await self._pool.disconnect()
        logger.info("Redis connection closed")
    
    async def is_connected(self) -> bool:
        """Check if Redis is connected."""
        try:
            if self._client:
                await self._client.ping()
                return True
        except Exception as e:
            logger.warning(f"Redis ping failed in is_connected: {e}")
        return False
    
    def _task_key(self, task_id: str) -> str:
        """Get Redis key for task data."""
        return f"task:{task_id}"
    
    def _progress_channel(self, task_id: str) -> str:
        """Get Redis channel for progress updates."""
        return f"progress:{task_id}"
    
    async def create_task(self, task_id: str, initial_data: Dict[str, Any]) -> None:
        """Create a new task in Redis."""
        key = self._task_key(task_id)
        
        task_data = {
            "task_id": task_id,
            "status": TaskStatus.PENDING.value,
            "progress": "0",
            "message": "Task created",
            "created_at": datetime.utcnow().isoformat(),
            "completed_at": "",
            "sources": json.dumps(initial_data.get("sources", [])),
            "request": json.dumps(initial_data.get("request", {})),
            "result": "",
            "error": ""
        }
        
        await self._client.hset(key, mapping=task_data)
        await self._client.expire(key, TASK_TTL_SECONDS)
        logger.debug(f"Created task: {task_id}")
    
    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task data from Redis."""
        key = self._task_key(task_id)
        data = await self._client.hgetall(key)
        
        if not data:
            return None
        
        # Deserialize JSON fields
        if data.get("sources"):
            data["sources"] = json.loads(data["sources"])
        if data.get("request"):
            data["request"] = json.loads(data["request"])
        if data.get("result"):
            data["result"] = json.loads(data["result"])
        
        return data
    
    async def update_task_status(
        self, 
        task_id: str, 
        status: TaskStatus, 
        progress: int = 0,
        message: str = ""
    ) -> None:
        """Update task status and publish progress."""
        key = self._task_key(task_id)
        
        updates = {
            "status": status.value,
            "progress": progress,
            "message": message
        }
        
        if status == TaskStatus.COMPLETED or status == TaskStatus.FAILED:
            updates["completed_at"] = datetime.utcnow().isoformat()
        
        await self._client.hset(key, mapping=updates)
        
        # Publish progress update
        progress_update = ProgressUpdate(
            task_id=task_id,
            status=status,
            progress=progress,
            total=100,
            message=message
        )
        
        await self._publish_progress(task_id, progress_update)
        logger.debug(f"Task {task_id}: {status.value} - {progress}% - {message}")
    
    async def set_task_result(self, task_id: str, result: Dict[str, Any]) -> None:
        """Store task result."""
        key = self._task_key(task_id)
        await self._client.hset(key, "result", json.dumps(result))
        logger.debug(f"Stored result for task: {task_id}")
    
    async def set_task_error(self, task_id: str, error: str) -> None:
        """Store task error."""
        key = self._task_key(task_id)
        await self._client.hset(key, mapping={
            "status": TaskStatus.FAILED.value,
            "error": error,
            "completed_at": datetime.utcnow().isoformat()
        })
        
        # Publish error update
        progress_update = ProgressUpdate(
            task_id=task_id,
            status=TaskStatus.FAILED,
            progress=0,
            total=100,
            message=f"Error: {error}"
        )
        await self._publish_progress(task_id, progress_update)
        logger.error(f"Task {task_id} failed: {error}")
    
    async def _publish_progress(self, task_id: str, update: ProgressUpdate) -> None:
        """Publish progress update to Redis channel."""
        channel = self._progress_channel(task_id)
        await self._client.publish(channel, update.model_dump_json())
    
    @asynccontextmanager
    async def subscribe_to_progress(self, task_id: str):
        """Subscribe to task progress updates."""
        channel = self._progress_channel(task_id)
        pubsub = self._pubsub_client.pubsub()
        
        try:
            await pubsub.subscribe(channel)
            yield pubsub
        finally:
            await pubsub.unsubscribe(channel)
            await pubsub.aclose()
    
    async def delete_task(self, task_id: str) -> bool:
        """Delete a task from Redis."""
        key = self._task_key(task_id)
        deleted = await self._client.delete(key)
        return deleted > 0


# Convenience functions
async def get_redis_store() -> RedisTaskStore:
    """Dependency injection for Redis store."""
    return await RedisTaskStore.get_instance()
