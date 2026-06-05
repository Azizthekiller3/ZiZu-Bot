import motor.motor_asyncio
from datetime import datetime, date
from info import DATABASE_URI, DATABASE_NAME

_client = motor.motor_asyncio.AsyncIOMotorClient(DATABASE_URI)
_db = _client[DATABASE_NAME]

_cfg_col   = _db["shortlink_config"]
_users_col = _db["shortlink_users"]


# ── Config ─────────────────────────────────────────────────────────────────────

async def get_shortlink_config():
    """Return the stored shortlink config dict or None."""
    return await _cfg_col.find_one({"_id": "config"}, {"_id": 0})


async def set_shortlink_config(domain: str, api_key: str):
    await _cfg_col.update_one(
        {"_id": "config"},
        {"$set": {"domain": domain, "api_key": api_key}},
        upsert=True,
    )


async def set_daily_verify(count: int):
    await _cfg_col.update_one(
        {"_id": "config"},
        {"$set": {"daily_verify": count}},
        upsert=True,
    )


async def get_daily_verify() -> int:
    cfg = await _cfg_col.find_one({"_id": "config"})
    if cfg:
        return int(cfg.get("daily_verify", 1))
    return 1


# ── Per-user verification tracking ────────────────────────────────────────────

async def get_user_verify(user_id: int) -> dict:
    doc = await _users_col.find_one({"user_id": user_id})
    today = str(date.today())
    if not doc or doc.get("date") != today:
        return {"user_id": user_id, "date": today, "count": 0}
    return doc


async def increment_verify(user_id: int):
    today = str(date.today())
    await _users_col.update_one(
        {"user_id": user_id},
        {"$set": {"date": today}, "$inc": {"count": 1}},
        upsert=True,
    )


async def needs_verify(user_id: int) -> bool:
    """Return True if user still needs to complete a shortlink today."""
    cfg = await get_shortlink_config()
    if not cfg or not cfg.get("domain"):
        return False
    daily = int(cfg.get("daily_verify", 1))
    uv = await get_user_verify(user_id)
    return uv["count"] < daily
