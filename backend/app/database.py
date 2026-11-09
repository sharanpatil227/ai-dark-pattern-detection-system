"""
MongoDB database connection using Motor (async driver).
Provides connection management and database/collection access.
"""

import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings

logger = logging.getLogger(__name__)

# Global database client and reference
_client: AsyncIOMotorClient | None = None
_database: AsyncIOMotorDatabase | None = None


async def connect_to_mongodb() -> None:
    """Establish connection to MongoDB. Logs warning if connection fails."""
    global _client, _database
    try:
        _client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=5000,
        )
        # Verify connection is alive
        await _client.admin.command("ping")
        _database = _client[settings.DB_NAME]

        # Ensure indexes
        await _database.scans.create_index("scan_id", unique=True)
        await _database.scans.create_index("scanned_at")
        await _database.scans.create_index("url")

        logger.info("Connected to MongoDB at %s", settings.MONGODB_URI)
    except Exception as e:
        logger.warning(
            "Could not connect to MongoDB: %s. "
            "The API will still work for scanning but results will not be persisted.",
            e,
        )
        _client = None
        _database = None


async def close_mongodb_connection() -> None:
    """Close the MongoDB connection."""
    global _client, _database
    if _client is not None:
        _client.close()
        _client = None
        _database = None
        logger.info("Closed MongoDB connection.")


def get_database() -> AsyncIOMotorDatabase | None:
    """Return the database instance, or None if not connected."""
    return _database


async def is_db_connected() -> bool:
    """Check if the database connection is alive."""
    if _client is None:
        return False
    try:
        await _client.admin.command("ping")
        return True
    except Exception:
        return False
