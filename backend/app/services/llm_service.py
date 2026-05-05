"""
Google Gemini LLM service.
Handles interactions with Google's Generative AI API for embeddings and chat completions.
"""

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
        self.model_name = "gemini-pro"
        self.embedding_model = "models/embedding-001"

    async def generate_embeddings(self, text: str) -> list[float]:
        """
        Generate embeddings for a given text using Gemini API.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding vector
        """
        try:
            response = genai.embed_content(
                model=self.embedding_model,
                content=text,
            )
            return response["embedding"]
        except Exception as e:
            print(f"✗ Error generating embeddings: {e}")
            raise

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
            raise

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


# Dependency injection function
async def get_llm_service() -> LLMService:
    """Dependency injection for LLM service."""
    return LLMService()
