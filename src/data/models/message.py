"""This file contains the message model for the application."""

from typing import (
    TYPE_CHECKING,
    Optional,
)

from sqlmodel import (
    Field,
    Relationship,
)

from src.data.models.base import BaseModel

if TYPE_CHECKING:
    from src.data.models.session import Session


class Message(BaseModel, table=True):
    """Message model for storing chat history and agent reports.

    Attributes:
        id: The primary key
        session_id: Foreign key to the session
        agent_role: Role of the agent that generated the message (e.g., "Sponsor Agent")
        content: Content of the message/report
        type: Type of message (e.g., "report", "chat", "summary")
        session: Relationship to the owning session
    """

    id: int = Field(default=None, primary_key=True)
    session_id: str = Field(foreign_key="session.id")
    agent_role: str = Field(index=True)
    content: str
    type: str = Field(default="report")

    session: "Session" = Relationship(back_populates="messages")
