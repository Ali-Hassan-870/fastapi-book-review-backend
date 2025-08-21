# import redis.asyncio as redis
from src.config import Config
import fakeredis.aioredis

JTI_EXPIRY = 3600

token_blocklist = fakeredis.aioredis.FakeRedis(
    host=Config.REDIS_HOST, 
    port=Config.REDIS_PORT, 
    db=0,
    decode_responses=True
)

async def add_token_to_blocklist(jti: str) -> None:
    await token_blocklist.set(name=jti, value="", ex=JTI_EXPIRY)

async def is_token_in_blocklist(jti: str) -> bool:
    result = await token_blocklist.get(jti)
    return result is not None