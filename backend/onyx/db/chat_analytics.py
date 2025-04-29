from datetime import datetime
from typing import List
from typing import Tuple

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session


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
) -> List[Tuple[str, int]]:
    """
    Fetch chat sessions grouped by user email.

    Args:
        db_session: Database session
        start_time: Start time for filtering
        end_time: End time for filtering

    Returns:
        List of tuples containing (user_email, session_count)
    """
    if not check_table_exists(db_session, "chat_history"):
        return [("No chat history data available", 0)]

    try:
        query = text(
            """
            SELECT u.email, COUNT(DISTINCT ch.id) as session_count
            FROM chat_history ch
            JOIN users u ON ch.user_id = u.id
            WHERE ch.created_at BETWEEN :start_time AND :end_time
            GROUP BY u.email
            ORDER BY session_count DESC
        """
        )

        result = db_session.execute(
            query, {"start_time": start_time, "end_time": end_time}
        )
        return [(row[0], row[1]) for row in result]
    except SQLAlchemyError as e:
        return [(f"Error fetching data: {str(e)}", 0)]


def fetch_chat_sessions_by_assistant(
    db_session: Session, start_time: datetime, end_time: datetime
) -> List[Tuple[str, int]]:
    """
    Fetch chat sessions grouped by assistant name.

    Args:
        db_session: Database session
        start_time: Start time for filtering
        end_time: End time for filtering

    Returns:
        List of tuples containing (assistant_name, session_count)
    """
    if not check_table_exists(db_session, "chat_history"):
        return [("No chat history data available", 0)]

    try:
        query = text(
            """
            SELECT COALESCE(ch.assistant_name, 'Default Assistant') as assistant,
                COUNT(DISTINCT ch.id) as session_count
            FROM chat_history ch
            WHERE ch.created_at BETWEEN :start_time AND :end_time
            GROUP BY assistant
            ORDER BY session_count DESC
        """
        )

        result = db_session.execute(
            query, {"start_time": start_time, "end_time": end_time}
        )
        return [(row[0], row[1]) for row in result]
    except SQLAlchemyError as e:
        return [(f"Error fetching data: {str(e)}", 0)]
