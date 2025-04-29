from datetime import datetime
from http import HTTPStatus

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from onyx.auth.users import current_admin_user
from onyx.configs.app_configs import ONYX_QUERY_HISTORY_TYPE
from onyx.configs.constants import QueryHistoryType
from onyx.db.chat_analytics import fetch_chat_sessions_by_assistant
from onyx.db.chat_analytics import fetch_chat_sessions_by_user
from onyx.db.engine import get_session
from onyx.db.models import User
from onyx.server.manage.models import ChatSessionGroupData
from onyx.server.manage.models import ChatSessionGroupRequest
from onyx.server.manage.models import ChatSessionGroupResponse
from onyx.server.manage.models import GroupingType

router = APIRouter(prefix="/admin")


@router.post("/chat-session-groups")
def get_chat_session_groups(
    request: ChatSessionGroupRequest,
    _: User | None = Depends(current_admin_user),
    db_session: Session = Depends(get_session),
) -> ChatSessionGroupResponse:
    """Get chat sessions grouped by user or assistant."""
    if ONYX_QUERY_HISTORY_TYPE == QueryHistoryType.DISABLED:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Query history has been disabled by the administrator.",
        )

    try:
        start_time = datetime.fromisoformat(request.start_time)
        end_time = datetime.fromisoformat(request.end_time)
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Invalid datetime format. Use ISO format."
        )

    if request.grouping_type == GroupingType.USER:
        results = fetch_chat_sessions_by_user(db_session, start_time, end_time)
    else:
        results = fetch_chat_sessions_by_assistant(db_session, start_time, end_time)

    total_sessions = sum(count for _, count in results)

    data = [ChatSessionGroupData(name=name, count=count) for name, count in results]

    return ChatSessionGroupResponse(
        data=data, total_rows=len(data), total_sessions=total_sessions
    )
