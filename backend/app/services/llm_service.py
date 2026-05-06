"""
Google Gemini LLM service.
Handles interactions with Google's Generative AI API for embeddings and chat completions.
"""

import hashlib

import google.generativeai as genai
from app.core.config import settings


class LLMService:
    """
    Service for interacting with Google Gemini API.
    Provides methods for embeddings and chat completions.
    """

    def __init__(self):
        """Initialize Google Gemini API with the configured API key."""
        genai.configure(api_key=settings.google_api_key)
        self.model_name = "models/gemini-2.5-flash"
        self.embedding_model = "models/gemini-embedding-001"

    async def generate_embeddings(
        self, text: str, task_type: str | None = None
    ) -> list[float]:
        """
        Generate embeddings for a given text using Gemini API.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding vector
        """
        try:
            embed_kwargs = {
                "model": self.embedding_model,
                "content": text,
                "output_dimensionality": 1024,
            }
            if task_type:
                embed_kwargs["task_type"] = task_type

            response = genai.embed_content(**embed_kwargs)
            return response["embedding"]
        except Exception as e:
            print(f"✗ Error generating embeddings: {e}")
            return self._local_embedding(text)

    async def generate_answer(
        self, question: str, context: str, system_prompt: str = None
    ) -> str:
        """
        Generate an answer using Gemini based on context and question.

        Args:
            question: The user's question
            context: Retrieved context from vector store
            system_prompt: Optional system prompt for the model

        Returns:
            Generated answer as string
        """
        try:
            model = genai.GenerativeModel(
                self.model_name,
                system_instruction=system_prompt
                or "You are a helpful AI assistant. Answer questions based on the provided context.",
            )

            prompt = f"""Context:
{context}

Question: {question}

Please provide a clear and concise answer based on the context provided."""

            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"✗ Error generating answer: {e}")
            return self._fallback_answer(question, context, str(e))

    async def summarize_text(self, text: str) -> str:
        """
        Summarize provided text using Gemini.

        Args:
            text: Text to summarize

        Returns:
            Summarized text
        """
        try:
            model = genai.GenerativeModel(self.model_name)
            prompt = f"Please provide a concise summary of the following text:\n\n{text}"
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"✗ Error summarizing text: {e}")
            raise

    def _fallback_answer(self, question: str, context: str, error_message: str = "") -> str:
        """Provide a deterministic fallback answer when Gemini generation is unavailable."""
        source_lines = [line.strip() for line in context.splitlines() if line.strip().startswith("Source:")]
        sources = [line.replace("Source:", "").strip() for line in source_lines]
        unique_sources = []
        for source in sources:
            if source and source not in unique_sources:
                unique_sources.append(source)

        source_summary = ", ".join(unique_sources[:3]) if unique_sources else "the uploaded documents"

        lowered_error = (error_message or "").lower()
        if "quota exceeded" in lowered_error or "429" in lowered_error:
            return (
                "Gemini API quota is exhausted for this API key, so live answer generation is currently unavailable. "
                "Enable billing or use a key with available quota, then retry. "
                f"Relevant context was found in: {source_summary}."
            )

        return (
            f"I found relevant context in {source_summary}, but live model generation is currently unavailable. "
            f"Please retry in a moment. Question received: {question}"
        )

    def _local_embedding(self, text: str, dimensions: int = 1024) -> list[float]:
        """Generate a deterministic fallback embedding for local/testing use."""
        embedding = []

        for index in range(dimensions):
            digest = hashlib.sha256(f"{text}:{index}".encode("utf-8")).digest()
            value = int.from_bytes(digest[:4], "big") / 2**32
            embedding.append((value * 2.0) - 1.0)

        return embedding


# Dependency injection function
async def get_llm_service() -> LLMService:
    """Dependency injection for LLM service."""
    return LLMService()
