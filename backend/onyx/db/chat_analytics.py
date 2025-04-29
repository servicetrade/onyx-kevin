from datetime import datetime
from typing import List
from typing import Tuple

from sqlalchemy import text
from sqlalchemy.orm import Session


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

    result = db_session.execute(query, {"start_time": start_time, "end_time": end_time})

    return [(row[0], row[1]) for row in result]


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

    result = db_session.execute(query, {"start_time": start_time, "end_time": end_time})

    return [(row[0], row[1]) for row in result]
