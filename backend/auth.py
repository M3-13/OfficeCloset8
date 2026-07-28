from fastapi import HTTPException


def hash_password(password: str) -> str:
    raise NotImplementedError


def verify_password(password: str, hashed: str) -> bool:
    raise NotImplementedError


def create_session(user_id: int) -> str:
    raise NotImplementedError


def get_current_user():
    raise HTTPException(status_code=401, detail="Not authenticated")


def require_auth():
    raise HTTPException(status_code=401, detail="Not authenticated")
