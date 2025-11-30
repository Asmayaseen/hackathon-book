"""
Pydantic models for chat API requests and responses.

Defines the data structures for chatbot interactions including
queries, responses, messages, and source citations.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class SourceCitation(BaseModel):
    """
    Source citation for RAG responses.

    Tracks where retrieved information came from in the textbook.
    """

    module: str = Field(..., description="Module name (e.g., 'Module 1: ROS 2')")
    chapter: str = Field(..., description="Chapter title")
    section: Optional[str] = Field(None, description="Section within chapter (if applicable)")
    url: str = Field(..., description="URL to the specific page in the textbook")
    relevance_score: float = Field(..., description="Similarity score from vector search (0-1)")

    class Config:
        json_schema_extra = {
            "example": {
                "module": "Module 1: ROS 2 Fundamentals",
                "chapter": "Week 3: Nodes and Topics",
                "section": "Creating Publishers",
                "url": "https://yourusername.github.io/hackathon-book/module-01-ros2/week-3-nodes-topics#publishers",
                "relevance_score": 0.87
            }
        }


class ChatMessage(BaseModel):
    """
    Individual message in a conversation.

    Represents either a user query or assistant response.
    """

    role: str = Field(..., description="Message sender: 'user' or 'assistant'")
    content: str = Field(..., description="Message text content")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When message was created")
    sources: Optional[List[SourceCitation]] = Field(None, description="Source citations (assistant messages only)")

    class Config:
        json_schema_extra = {
            "example": {
                "role": "assistant",
                "content": "ROS 2 nodes communicate via topics using a publish-subscribe pattern...",
                "timestamp": "2025-11-29T10:30:00Z",
                "sources": [
                    {
                        "module": "Module 1: ROS 2 Fundamentals",
                        "chapter": "Week 3: Nodes and Topics",
                        "url": "/module-01-ros2/week-3-nodes-topics",
                        "relevance_score": 0.87
                    }
                ]
            }
        }


class ChatRequest(BaseModel):
    """
    Request payload for chat query endpoint.

    Contains user's question and optional conversation context.
    """

    query: str = Field(..., min_length=1, max_length=2000, description="User's question or prompt")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID for context")
    selected_text: Optional[str] = Field(None, description="Text selected by user (if asking about specific content)")
    module_filter: Optional[str] = Field(None, description="Optional filter to search only specific module")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "How do ROS 2 nodes communicate with each other?",
                "conversation_id": "conv_abc123",
                "selected_text": None,
                "module_filter": "module-01-ros2"
            }
        }


class ChatResponse(BaseModel):
    """
    Response payload from chat query endpoint.

    Contains AI-generated answer with source citations and metadata.
    """

    answer: str = Field(..., description="AI-generated response to user's query")
    sources: List[SourceCitation] = Field(default_factory=list, description="Sources used to generate answer")
    conversation_id: str = Field(..., description="Conversation ID for follow-up context")
    processing_time: float = Field(..., description="Time taken to process query (seconds)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "ROS 2 nodes communicate via topics using a publish-subscribe pattern. Publishers send messages to topics, and subscribers receive them asynchronously. [Module 1: Week 3]",
                "sources": [
                    {
                        "module": "Module 1: ROS 2 Fundamentals",
                        "chapter": "Week 3: Nodes and Topics",
                        "url": "/module-01-ros2/week-3-nodes-topics",
                        "relevance_score": 0.87
                    }
                ],
                "conversation_id": "conv_abc123",
                "processing_time": 1.23,
                "timestamp": "2025-11-29T10:30:00Z"
            }
        }
