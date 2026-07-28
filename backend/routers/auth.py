import logging
import re
from typing import Annotated

from auth import COOKIE_NAME, get_current_user, hash_password, verify_password
from auth import create_session as auth_create_session
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from models import Session, User
from schemas import UserCreate, UserResponse
from sqlalchemy.orm import Session as DBSession

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")
MAX_EMAIL_LENGTH = 254
MIN_PASSWORD_LENGTH = 8


@router.post("/register", status_code=201, response_model=UserResponse)
def register(
    body: UserCreate,
    response: Response,
    db: Annotated[DBSession, Depends(get_db)],
):
    email = body.email.lower().strip()
    password = body.password.strip()

    if len(email) > MAX_EMAIL_LENGTH:
        raise HTTPException(status_code=422, detail="E-Mail zu lang (max. 254 Zeichen)")
    if not EMAIL_REGEX.match(email):
        raise HTTPException(status_code=422, detail="Ungültiges E-Mail-Format")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise HTTPException(status_code=422, detail="Passwort muss mindestens 8 Zeichen lang sein")

    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=409, detail="E-Mail bereits registriert")

    user = User(email=email, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info("User %s registered", user.id)
    auth_create_session(response, user.id, db)
    return user


@router.post("/login", response_model=UserResponse)
def login(
    body: UserCreate,
    response: Response,
    db: Annotated[DBSession, Depends(get_db)],
):
    email = body.email.lower().strip()
    password = body.password.strip()

    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="E-Mail oder Passwort ungültig")

    logger.info("User %s logged in", user.id)
    auth_create_session(response, user.id, db)
    return user


@router.post("/logout", status_code=200)
def logout(
    request: Request,
    response: Response,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[DBSession, Depends(get_db)],
):
    token = request.cookies.get(COOKIE_NAME)
    if token:
        db.query(Session).filter(Session.token == token).delete()
        db.commit()
    response.delete_cookie(key=COOKIE_NAME, httponly=True, secure=True, samesite="lax")
    return {"message": "Logged out"}


@router.get("/me", response_model=UserResponse)
def me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user
