from fastapi import HTTPException, Request


def hash_password(password: str) -> str:
    raise NotImplementedError


def verify_password(password: str, password_hash: str) -> bool:
    raise NotImplementedError


def create_session(response, user_id: int) -> None:
    raise NotImplementedError


def get_current_user(request: Request) -> dict:
    raise HTTPException(status_code=401, detail="Not authenticated")


def require_auth(request: Request):
    return get_current_user(request)
