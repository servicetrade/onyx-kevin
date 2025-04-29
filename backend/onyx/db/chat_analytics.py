import datetime
from typing import List
from typing import Tuple

from sqlalchemy import desc
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.orm import Session

from onyx.db.models import ChatSession
from onyx.db.models import Persona
from onyx.db.models import User


def fetch_chat_sessions_by_user(
    db_session: Session,
    start: datetime.datetime,
    end: datetime.datetime,
) -> List[Tuple[str, int]]:
    """
    Gets the count of chat sessions for each user within the given time range.
    Returns a list of tuples containing (user_email, session_count)
    """
    query = (
        select(
            User.email,
            func.count(func.distinct(ChatSession.id)),
        )
        .join(User, ChatSession.user_id == User.id)
        .where(
            ChatSession.time_created >= start,
            ChatSession.time_created <= end,
        )
        .group_by(User.email)
        .order_by(desc(func.count(func.distinct(ChatSession.id))))
    )

    return [
        (row[0] if row[0] else "Anonymous", row[1])
        for row in db_session.execute(query).all()
    ]


def fetch_chat_sessions_by_assistant(
    db_session: Session,
    start: datetime.datetime,
    end: datetime.datetime,
) -> List[Tuple[str, int]]:
    """
    Gets the count of chat sessions for each assistant within the given time range.
    Returns a list of tuples containing (assistant_name, session_count)
    """
    query = (
        select(
            Persona.name,
            func.count(func.distinct(ChatSession.id)),
        )
        .join(Persona, ChatSession.persona_id == Persona.id, isouter=True)
        .where(
            ChatSession.time_created >= start,
            ChatSession.time_created <= end,
        )
        .group_by(Persona.name)
        .order_by(desc(func.count(func.distinct(ChatSession.id))))
    )

    return [
        (row[0] if row[0] else "No Assistant", row[1])
        for row in db_session.execute(query).all()
    ]
