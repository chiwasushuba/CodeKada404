"""
Pinecone vector store service.
Handles vector operations including storage, retrieval, and similarity search.
"""

from pinecone import Pinecone
from app.core.config import settings


class VectorService:
    """
    Service for managing vector operations with Pinecone.
    Handles embedding storage and semantic search.
    """

    def __init__(self):
        """Initialize Pinecone client and get index."""
        self.pc = Pinecone(api_key=settings.pinecone_api_key)
        self.index = self.pc.Index(settings.pinecone_index_name)

    async def upsert_vectors(
        self, vectors: list[dict], namespace: str = "default"
    ) -> dict:
        """
        Upsert (insert or update) vectors in Pinecone index.

        Args:
            vectors: List of vectors with format:
                    [{"id": "id1", "values": [...], "metadata": {...}}, ...]
            namespace: Namespace to upsert vectors into

        Returns:
            Response from Pinecone API
        """
        try:
            response = self.index.upsert(vectors=vectors, namespace=namespace)
            print(f"✓ Upserted {len(vectors)} vectors to Pinecone")
            return response
        except Exception as e:
            print(f"✗ Error upserting vectors: {e}")
            raise

    async def query_vectors(
        self, query_vector: list[float], top_k: int = 5, namespace: str = "default"
    ) -> list[dict]:
        """
        Query similar vectors from Pinecone index.

        Args:
            query_vector: Vector to search for (embedding)
            top_k: Number of top results to return
            namespace: Namespace to query from

        Returns:
            List of matched vectors with metadata
        """
        try:
            results = self.index.query(
                vector=query_vector, top_k=top_k, namespace=namespace, include_metadata=True
            )
            return results.get("matches", [])
        except Exception as e:
            print(f"✗ Error querying vectors: {e}")
            raise

    async def delete_vectors(
        self, vector_ids: list[str], namespace: str = "default"
    ) -> dict:
        """
        Delete vectors from Pinecone index.

        Args:
            vector_ids: List of vector IDs to delete
            namespace: Namespace to delete from

        Returns:
            Response from Pinecone API
        """
        try:
            response = self.index.delete(ids=vector_ids, namespace=namespace)
            print(f"✓ Deleted {len(vector_ids)} vectors from Pinecone")
            return response
        except Exception as e:
            print(f"✗ Error deleting vectors: {e}")
            raise

    async def get_index_stats(self) -> dict:
        """
        Get statistics about the Pinecone index.

        Returns:
            Index statistics
        """
        try:
            stats = self.index.describe_index_stats()
            return stats
        except Exception as e:
            print(f"✗ Error getting index stats: {e}")
            raise


# Dependency injection function
async def get_vector_service() -> VectorService:
    """Dependency injection for vector service."""
    return VectorService()
