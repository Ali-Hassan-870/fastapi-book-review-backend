import redis.asyncio as redis
from src.config import Config

JTI_EXPIRY = 3600

token_blocklist = redis.from_url(
    url=Config.REDIS_URL,
)


async def add_token_to_blocklist(jti: str) -> None:
    await token_blocklist.set(name=jti, value="", ex=JTI_EXPIRY)


async def is_token_in_blocklist(jti: str) -> bool:
    result = await token_blocklist.get(jti)
    return result is not None
