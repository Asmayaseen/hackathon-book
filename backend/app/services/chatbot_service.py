"""
Chatbot service for generating AI responses using GPT-4.

Orchestrates RAG pipeline: retrieves context, formats prompt,
generates response with source citations.
"""

import logging
from typing import List, Dict
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
import uuid

from app.config import settings
from app.services.rag_service import rag_service
from app.models.chat import ChatResponse, SourceCitation

logger = logging.getLogger(__name__)


class ChatbotService:
    """
    Service for generating chatbot responses using RAG pipeline.

    Combines vector search (RAG) with GPT-4 to provide accurate,
    source-cited answers to user questions about the textbook.
    """

    def __init__(self):
        """Initialize OpenAI client with API key from settings."""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_chat_model
        logger.info(f"Initialized ChatbotService with model: {self.model}")

        # System prompt for GPT-4 to guide response generation
        self.system_prompt = """You are a helpful AI tutor for Physical AI and Humanoid Robotics.

Your role is to answer student questions based on the course textbook content provided to you.

Guidelines:
1. Answer ONLY using the provided context from the textbook
2. If the context doesn't contain relevant information, say so clearly
3. Always cite sources using the format: [Module X: Chapter Name]
4. Be concise but thorough - aim for 2-4 paragraphs
5. Use technical terms appropriately for the student's level
6. Include code examples from context when relevant
7. If asked about specific implementations, refer to the relevant module

Remember: You are teaching Physical AI concepts (ROS 2, Gazebo, NVIDIA Isaac, VLA).
Be accurate, educational, and always cite your sources."""

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True
    )
    def generate_response(
        self,
        query: str,
        conversation_id: str = None,
        selected_text: str = None,
        module_filter: str = None
    ) -> ChatResponse:
        """
        Generate AI response to user query using RAG pipeline.

        Process:
        1. Retrieve relevant passages from Qdrant
        2. Format context and user query into prompt
        3. Call GPT-4 to generate response
        4. Format response with source citations

        Args:
            query: User's question
            conversation_id: Optional conversation ID for context
            selected_text: Text user selected (prioritized in context)
            module_filter: Optional filter to search specific module only

        Returns:
            ChatResponse with answer, sources, timing metadata

        Raises:
            Exception if retrieval or generation fails
        """
        import time
        start_time = time.time()

        try:
            # Step 1: Retrieve relevant passages via RAG
            logger.info(f"Processing query: {query[:100]}...")

            # If user selected text, use it as priority context
            if selected_text:
                logger.info(f"User selected text: {selected_text[:100]}...")

            passages = rag_service.retrieve_relevant_passages(
                query=query,
                module_filter=module_filter
            )

            if not passages:
                # No relevant content found
                logger.warning("No relevant passages found for query")
                return ChatResponse(
                    answer="I couldn't find relevant information in the textbook to answer your question. Could you rephrase or ask about a different topic covered in the Physical AI course?",
                    sources=[],
                    conversation_id=conversation_id or str(uuid.uuid4()),
                    processing_time=time.time() - start_time
                )

            # Step 2: Format context for GPT-4
            context = self._format_context(passages, selected_text)

            # Step 3: Generate response with GPT-4
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Context from textbook:\n\n{context}\n\nStudent question: {query}"}
            ]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,  # Balanced creativity/consistency
                max_tokens=800,  # Allow detailed responses
                top_p=0.9
            )

            answer = response.choices[0].message.content

            # Step 4: Format source citations
            sources = self._create_source_citations(passages)

            processing_time = time.time() - start_time
            logger.info(f"Generated response in {processing_time:.2f}s")

            return ChatResponse(
                answer=answer,
                sources=sources,
                conversation_id=conversation_id or str(uuid.uuid4()),
                processing_time=processing_time
            )

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise

    def _format_context(self, passages: List[Dict], selected_text: str = None) -> str:
        """
        Format retrieved passages into context string for GPT-4.

        Args:
            passages: List of passage dicts from RAG retrieval
            selected_text: Optional user-selected text to prioritize

        Returns:
            Formatted context string with module/chapter headers
        """
        context_parts = []

        # Prioritize selected text if provided
        if selected_text:
            context_parts.append(f"[User Selected Text]\n{selected_text}\n")

        # Add retrieved passages
        for i, passage in enumerate(passages, 1):
            header = f"[{passage['module']} - {passage['chapter']}"
            if passage.get('section'):
                header += f" - {passage['section']}"
            header += "]"

            context_parts.append(f"{header}\n{passage['text']}\n")

        return "\n---\n".join(context_parts)

    def _create_source_citations(self, passages: List[Dict]) -> List[SourceCitation]:
        """
        Convert passage metadata into SourceCitation objects.

        Args:
            passages: List of passage dicts from RAG retrieval

        Returns:
            List of SourceCitation objects for response
        """
        sources = []

        for passage in passages:
            source = SourceCitation(
                module=passage['module'],
                chapter=passage['chapter'],
                section=passage.get('section'),
                url=passage['url'],
                relevance_score=passage['score']
            )
            sources.append(source)

        return sources


# Singleton instance for dependency injection
chatbot_service = ChatbotService()
