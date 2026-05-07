"""
MongoDB database service using Motor (async MongoDB driver).
Handles all database operations and connection management.
"""

import motor.motor_asyncio
from uuid import uuid4
from app.core.config import settings

try:
    from bson import ObjectId
except Exception:  # pragma: no cover - optional runtime dependency in mock mode
    ObjectId = None

try:
    from pymongo import ReturnDocument
except Exception:  # pragma: no cover - optional runtime dependency in mock mode
    ReturnDocument = None


class DatabaseService:
    """
    Service for managing MongoDB connections and database operations.
    Uses Motor for async/await support.
    """

    client: object = None
    database: object = None
    mock_documents: dict[str, dict] = {}

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
        if cls.database is None:
            return f"mock-status-{uuid4()}"

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
        if cls.database is None:
            return []

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
        if cls.database is None:
            document_id = f"mock-document-{uuid4()}"
            document = {"id": document_id, **metadata}
            cls.mock_documents[document_id] = document
            return document_id

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
        if cls.database is None:
            return None

        documents_collection = cls.database["documents"]
        return await documents_collection.find_one({"file_name": file_name})

    @classmethod
    async def list_knowledge_files(cls) -> list[dict]:
        """
        Retrieve all uploaded file metadata used by context verification.

        MongoDB integration note:
        - Ensure documents collection stores: file_name, ai_context, is_verified, r2_path.
        - Return documents sorted by uploaded_at descending.
        - TODO: Replace mock fallback with your real Motor collection reads in production.
        """
        if cls.database is None:
            documents = list(cls.mock_documents.values())
            return sorted(documents, key=lambda item: item.get("uploaded_at", ""), reverse=True)

        documents_collection = cls.database["documents"]
        cursor = documents_collection.find().sort("uploaded_at", -1)
        documents = await cursor.to_list(length=1000)

        normalized = []
        for document in documents:
            normalized.append({
                "id": str(document.get("_id")),
                "file_name": document.get("file_name", "Unknown"),
                "ai_context": document.get("ai_context")
                or document.get("manual_context")
                or document.get("text_preview", ""),
                "is_verified": bool(document.get("is_verified", False)),
                "r2_path": document.get("r2_path", ""),
                "uploaded_at": document.get("uploaded_at", ""),
            })
        return normalized

    @classmethod
    async def get_knowledge_file_by_id(cls, file_id: str) -> dict | None:
        """Retrieve knowledge metadata by file ID."""
        if cls.database is None:
            return cls.mock_documents.get(file_id)

        documents_collection = cls.database["documents"]
        query = None

        if ObjectId:
            try:
                query = {"_id": ObjectId(file_id)}
            except Exception:
                query = {"id": file_id}
        else:
            query = {"id": file_id}

        document = await documents_collection.find_one(query)
        if not document:
            return None

        return {
            "id": str(document.get("_id")),
            "file_name": document.get("file_name", "Unknown"),
            "ai_context": document.get("ai_context")
            or document.get("manual_context")
            or document.get("text_preview", ""),
            "is_verified": bool(document.get("is_verified", False)),
            "r2_path": document.get("r2_path", ""),
            "uploaded_at": document.get("uploaded_at", ""),
        }

    @classmethod
    async def mark_knowledge_file_verified(cls, file_id: str) -> dict | None:
        """Set knowledge file verification status to true."""
        if cls.database is None:
            document = cls.mock_documents.get(file_id)
            if not document:
                return None
            document["is_verified"] = True
            cls.mock_documents[file_id] = document
            return document

        documents_collection = cls.database["documents"]
        query = None

        if ObjectId:
            try:
                query = {"_id": ObjectId(file_id)}
            except Exception:
                query = {"id": file_id}
        else:
            query = {"id": file_id}

        result = await documents_collection.find_one_and_update(
            query,
            {"$set": {"is_verified": True}},
            return_document=ReturnDocument.AFTER if ReturnDocument else True,
        )

        if not result:
            return None

        return {
            "id": str(result.get("_id")),
            "is_verified": bool(result.get("is_verified", False)),
        }

    @classmethod
    async def update_knowledge_context(cls, file_id: str, manual_context: str) -> dict | None:
        """
        Update knowledge context text and reset verification.

        MongoDB integration note:
        - Persist `ai_context` with manual text to make corrected context the source of truth.
        - Keep `manual_context` if you want auditability/history in your schema.
        - TODO: Add audit fields (updated_by, updated_at, previous_context) for your production schema.
        """
        if cls.database is None:
            document = cls.mock_documents.get(file_id)
            if not document:
                return None
            document["ai_context"] = manual_context
            document["manual_context"] = manual_context
            document["is_verified"] = False
            cls.mock_documents[file_id] = document
            return document

        documents_collection = cls.database["documents"]
        query = None

        if ObjectId:
            try:
                query = {"_id": ObjectId(file_id)}
            except Exception:
                query = {"id": file_id}
        else:
            query = {"id": file_id}

        result = await documents_collection.find_one_and_update(
            query,
            {
                "$set": {
                    "ai_context": manual_context,
                    "manual_context": manual_context,
                    "is_verified": False,
                }
            },
            return_document=ReturnDocument.AFTER if ReturnDocument else True,
        )

        if not result:
            return None

        return {
            "id": str(result.get("_id")),
            "file_name": result.get("file_name", "Unknown"),
            "ai_context": result.get("ai_context") or manual_context,
            "is_verified": bool(result.get("is_verified", False)),
            "r2_path": result.get("r2_path", ""),
        }

    @classmethod
    async def delete_knowledge_file_by_id(cls, file_id: str) -> dict | None:
        """Delete a knowledge file record by ID."""
        if cls.database is None:
            return cls.mock_documents.pop(file_id, None)

        documents_collection = cls.database["documents"]
        query = None

        if ObjectId:
            try:
                query = {"_id": ObjectId(file_id)}
            except Exception:
                query = {"id": file_id}
        else:
            query = {"id": file_id}

        result = await documents_collection.find_one_and_delete(query)
        if not result:
            return None

        return {
            "id": str(result.get("_id")),
            "file_name": result.get("file_name", "Unknown"),
            "r2_path": result.get("r2_path", ""),
        }

    @classmethod
    async def delete_documents_by_r2_path(cls, r2_path: str) -> dict:
        """Delete all documents whose r2_path matches the provided key.

        Returns a dict with deleted_count and deleted_ids (when available).
        """
        deleted_ids = []
        if cls.database is None:
            # Mock mode: remove any mock documents matching the r2_path
            to_delete = [doc_id for doc_id, doc in cls.mock_documents.items() if doc.get("r2_path") == r2_path]
            for doc_id in to_delete:
                cls.mock_documents.pop(doc_id, None)
                deleted_ids.append(doc_id)
            return {"deleted_count": len(deleted_ids), "deleted_ids": deleted_ids}

        documents_collection = cls.database["documents"]
        # Find documents to collect IDs (if ObjectId is available, convert)
        cursor = documents_collection.find({"r2_path": r2_path})
        found = await cursor.to_list(length=1000)
        for doc in found:
            deleted_ids.append(str(doc.get("_id")))

        result = await documents_collection.delete_many({"r2_path": r2_path})
        deleted_count = int(getattr(result, "deleted_count", 0) or 0)
        return {"deleted_count": deleted_count, "deleted_ids": deleted_ids}


# Dependency injection function
async def get_db_service() -> DatabaseService:
    """Dependency injection for database service."""
    return DatabaseService
