"""
MongoDB database service using Motor (async MongoDB driver).
Handles all database operations and connection management.
"""

import motor.motor_asyncio
from app.core.config import settings


class DatabaseService:
    """
    Service for managing MongoDB connections and database operations.
    Uses Motor for async/await support.
    """

    client: object = None
    database: object = None

    @classmethod
    async def connect_db(cls) -> None:
        """
        Initialize MongoDB connection.
        Called on application startup.
        """
        try:
            # TODO: Fix Motor AsyncClient import issue
            # For now, skipping MongoDB connection for hackathon
            print("✓ MongoDB connection skipped (using mock data)")
            return
        except Exception as e:
            print(f"✗ Failed to connect to MongoDB: {e}")
            raise

    @classmethod
    async def close_db(cls) -> None:
        """
        Close MongoDB connection.
        Called on application shutdown.
        """
        if cls.client:
            cls.client.close()
            print("✓ MongoDB connection closed")

    @classmethod
    async def get_database(cls) -> object:
        """Get the current database instance."""
        return cls.database

    # ============= STATUS COLLECTION OPERATIONS =============

    @classmethod
    async def save_status_update(cls, update_data: dict) -> str:
        """
        Save a developer status update to MongoDB.

        Args:
            update_data: Dictionary containing status update information

        Returns:
            Inserted document ID as string
        """
        statuses_collection = cls.database["statuses"]
        result = await statuses_collection.insert_one(update_data)
        return str(result.inserted_id)

    @classmethod
    async def get_status_updates(cls, limit: int = 10) -> list[dict]:
        """
        Retrieve recent status updates from MongoDB.

        Args:
            limit: Maximum number of documents to retrieve

        Returns:
            List of status update documents
        """
        statuses_collection = cls.database["statuses"]
        cursor = statuses_collection.find().sort("timestamp", -1).limit(limit)
        return await cursor.to_list(length=limit)

    # ============= DOCUMENTS COLLECTION OPERATIONS =============

    @classmethod
    async def save_document_metadata(cls, metadata: dict) -> str:
        """
        Save document metadata (file info, processing status, etc.).

        Args:
            metadata: Dictionary containing document metadata

        Returns:
            Inserted document ID as string
        """
        documents_collection = cls.database["documents"]
        result = await documents_collection.insert_one(metadata)
        return str(result.inserted_id)

    @classmethod
    async def get_document_by_name(cls, file_name: str) -> dict:
        """
        Retrieve document metadata by file name.

        Args:
            file_name: Name of the file to retrieve

        Returns:
            Document metadata or None
        """
        documents_collection = cls.database["documents"]
        return await documents_collection.find_one({"file_name": file_name})


# Dependency injection function
async def get_db_service() -> DatabaseService:
    """Dependency injection for database service."""
    return DatabaseService
