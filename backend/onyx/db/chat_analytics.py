from dataclasses import dataclass
from datetime import datetime
from typing import List
from typing import Optional

from sqlalchemy import text, select, func, desc, join
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from onyx.db.models import ChatSession, User, Persona


@dataclass
class ChatSessionsAnalyticsData:
    """Data class for chat sessions analytics results."""
    name: str
    count: int


def check_table_exists(db_session: Session, table_name: str) -> bool:
    """
    Check if a table exists in the database.

    Args:
        db_session: Database session
        table_name: Name of the table to check

    Returns:
        True if the table exists, False otherwise
    """
    query = text(
        """
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name = :table_name
        )
    """
    )

    try:
        result = db_session.execute(query, {"table_name": table_name})
        return result.scalar()
    except SQLAlchemyError:
        return False


def fetch_chat_sessions_by_user(
    db_session: Session, start_time: datetime, end_time: datetime
) -> List[ChatSessionsAnalyticsData]:
    """
    Fetch chat sessions grouped by user email.

    Args:
        db_session: Database session
        start_time: Start time for filtering
        end_time: End time for filtering

    Returns:
        List of ChatSessionsAnalyticsData objects with user email and session count

    Raises:
        SQLAlchemyError: If there's a database query error
    """
    if not check_table_exists(db_session, "chat_session"):
        return [ChatSessionsAnalyticsData(name="No chat history data available", count=0)]

    try:
        stmt = (
            select(User.email, func.count(ChatSession.id).label("session_count"))
            .join(ChatSession, User.id == ChatSession.user_id)
            .where(ChatSession.time_created.between(start_time, end_time))
            .group_by(User.email)
            .order_by(desc("session_count"))
        )

        result = db_session.execute(stmt)
        return [ChatSessionsAnalyticsData(name=row[0], count=row[1]) for row in result]
    except ProgrammingError as e:
        if "relation" in str(e) and "does not exist" in str(e):
            return [ChatSessionsAnalyticsData(name="No chat history data available", count=0)]
        raise
    except SQLAlchemyError:
        raise


def fetch_chat_sessions_by_assistant(
    db_session: Session, start_time: datetime, end_time: datetime
) -> List[ChatSessionsAnalyticsData]:
    """
    Fetch chat sessions grouped by assistant name.

    Args:
        db_session: Database session
        start_time: Start time for filtering
        end_time: End time for filtering

    Returns:
        List of ChatSessionsAnalyticsData objects with assistant name and session count
        
    Raises:
        SQLAlchemyError: If there's a database query error
    """
    if not check_table_exists(db_session, "chat_session"):
        return [ChatSessionsAnalyticsData(name="No chat history data available", count=0)]

    try:
        # Using func.coalesce to match the SQL COALESCE function
        stmt = (
            select(
                func.coalesce(Persona.name, "Default Assistant").label("assistant_name"),
                func.count(ChatSession.id.distinct()).label("session_count"),
            )
            .select_from(ChatSession)
            .outerjoin(Persona, ChatSession.persona_id == Persona.id)
            .where(ChatSession.time_created.between(start_time, end_time))
            .group_by("assistant_name")
            .order_by(desc("session_count"))
        )

        result = db_session.execute(stmt)
        return [ChatSessionsAnalyticsData(name=row[0], count=row[1]) for row in result]
    except ProgrammingError as e:
        if "relation" in str(e) and "does not exist" in str(e):
            return [ChatSessionsAnalyticsData(name="No chat history data available", count=0)]
        raise
    except SQLAlchemyError:
        raise
