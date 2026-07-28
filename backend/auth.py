import logging
import uuid
from typing import Annotated

import bcrypt
from database import get_db
from fastapi import Depends, HTTPException, Request, Response
from models import Session, User
from sqlalchemy.orm import Session as DBSession

logger = logging.getLogger(__name__)

COOKIE_NAME = "session"
COOKIE_MAX_AGE = 60 * 60 * 24 * 30  # 30 days


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def create_session(response: Response, user_id: int, db: DBSession) -> str:
    token = uuid.uuid4().hex
    session = Session(token=token, user_id=user_id)
    db.add(session)
    db.commit()
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        max_age=COOKIE_MAX_AGE,
        httponly=True,
        secure=True,
        samesite="lax",
    )
    return token


def get_current_user(
    request: Request,
    db: Annotated[DBSession, Depends(get_db)],
) -> User:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    session = db.query(Session).filter(Session.token == token).first()
    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = db.query(User).filter(User.id == session.user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


def require_auth(
    request: Request,
    db: Annotated[DBSession, Depends(get_db)],
) -> User:
    return get_current_user(request, db)
