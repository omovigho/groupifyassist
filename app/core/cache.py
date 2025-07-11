# app/core/cache.py
import os
import sys
import json

from pathlib import Path
from upstash_redis import Redis
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).resolve().parents[2]))

# Load env
current_dir = Path(__file__).parent
config_path = current_dir / "config.env"
load_dotenv(dotenv_path=config_path)

# Use environment variables for security
UPSTASH_REDIS_URL = os.getenv("UPSTASH_REDIS_URL")
UPSTASH_REDIS_TOKEN = os.getenv("UPSTASH_REDIS_TOKEN")

# Initialize Redis client
redis = Redis(url=UPSTASH_REDIS_URL, token=UPSTASH_REDIS_TOKEN)

# Set a value with expiration time (in seconds)
def set_cache(key: str, value: str, timeout: int = 60):
    redis.set(key, value, ex=timeout)

# Get a cached value
def get_cache(key: str) -> str | None:
    return redis.get(key)

# Delete a cached key
def delete_cache(key: str):
    redis.delete(key)

def store_temp_user(email: str, data: dict, timeout: int = 60):
    redis.set(f"pending_user_{email}", json.dumps(data), ex=timeout)

def get_temp_user(email: str) -> dict | None:
    raw = redis.get(f"pending_user_{email}")
    return json.loads(raw) if raw else None

def delete_temp_user(email: str):
    redis.delete(f"pending_user_{email}")
