from django_redis import get_redis_connection
import time
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parent / 'token_bucket.lua'

r = get_redis_connection('default')
with open(SCRIPT_PATH, 'r') as f:
    token_bucket_script = r.register_script(f.read())

def consume_token(
    identifier: str,
    capacity: int = 100,
    refill_rate: float = 10.0,
    tokens_requested: int = 1
) -> bool:
    result = token_bucket_script(
        keys=[f"bucket:{identifier}"],
        args=[capacity, refill_rate, time.time(), tokens_requested]
    )
    return bool(result)