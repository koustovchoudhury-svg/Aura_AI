import json, os
from datetime import datetime

class MemoryStore:
    def __init__(self):
        self._redis = None

    async def _get_redis(self):
        if not self._redis:
            import redis.asyncio as redis
            self._redis = redis.from_url(
                os.getenv("REDIS_URL","redis://redis:6379/0"), decode_responses=True
            )
        return self._redis

    async def get_facts(self, user_id: str, limit: int = 15) -> list:
        from packages.db.connection import AsyncSessionFactory
        from packages.db.models import MemoryFact
        from sqlalchemy import select
        async with AsyncSessionFactory() as session:
            result = await session.execute(
                select(MemoryFact).where(MemoryFact.user_id == user_id)
                .order_by(MemoryFact.created_at.desc()).limit(limit)
            )
            return result.scalars().all()

    async def save_turn(self, session_id: str, user_input: str,
                        response: str, intent: str) -> None:
        try:
            r = await self._get_redis()
            key  = f"session:{session_id}:history"
            turn = json.dumps({"user":user_input,"assistant":response,
                               "intent":intent,"ts":datetime.utcnow().isoformat()})
            await r.rpush(key, turn)
            await r.ltrim(key, -20, -1)
            await r.expire(key, 86400)
        except Exception:
            pass

    async def get_session_context(self, session_id: str) -> list:
        try:
            r   = await self._get_redis()
            raw = await r.lrange(f"session:{session_id}:history", -10, -1)
            turns = []
            for item in raw:
                t = json.loads(item)
                turns.append({"role":"user","content":t["user"]})
                turns.append({"role":"assistant","content":t["assistant"]})
            return turns
        except Exception:
            return []
