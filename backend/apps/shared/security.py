from fastapi import Header, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from apps.authService.repository import auth as repo
from apps.authService.schema.auth import UserGet
from typing import Optional


def verify_token(
    x_token: Optional[str] = Header(None, description="The session token from login"),
    session: Session = Depends(get_db),
) -> UserGet:
    """
    Dependency to verify the session token and return the current user.
    """
    if not x_token:
        raise HTTPException(
            status_code=401, detail="Session token (X-Token) is missing"
        )

    try:
        auth_session = repo.get_session_by_token(session, x_token)
        if not auth_session:
            raise HTTPException(status_code=401, detail="Invalid or expired session token")

        user = repo.get_user_complete_info(session, auth_session.user_id)
        if not user:
             raise HTTPException(status_code=401, detail="User account not found")

        return UserGet.model_validate(user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication error: {str(e)}")
