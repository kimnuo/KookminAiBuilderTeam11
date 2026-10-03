from fastapi import APIRouter, Header, HTTPException

from app.core.schemas import AuthRequest, AuthResult, ConsentRequest
from app.db import store
from app.features.auth.service import AuthError, login, signup, user_of

router = APIRouter(tags=["auth"])


def _bearer(authorization: str | None) -> str | None:
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    return authorization[7:].strip()


def _me(authorization: str | None) -> str:
    user_id = user_of(_bearer(authorization))
    if not user_id:
        raise HTTPException(status_code=401, detail="로그인이 필요해요.")
    return user_id


@router.post("/auth/signup", response_model=AuthResult, summary="가입 (닉네임 + 비밀번호)")
def signup_route(body: AuthRequest) -> AuthResult:
    try:
        return signup(body.nickname, body.password)
    except AuthError as exc:
        raise HTTPException(status_code=exc.status, detail=exc.message) from exc


@router.post("/auth/login", response_model=AuthResult, summary="로그인")
def login_route(body: AuthRequest) -> AuthResult:
    try:
        return login(body.nickname, body.password)
    except AuthError as exc:
        raise HTTPException(status_code=exc.status, detail=exc.message) from exc


@router.post("/auth/logout", summary="로그아웃 (이 토큰만 버린다)")
def logout_route(authorization: str | None = Header(None)) -> dict:
    token = _bearer(authorization)
    if token:
        store.drop_session(token)
    return {"ok": True}


@router.delete("/me", summary="내 계정과 서버에 있는 내 자료를 모두 지운다")
def delete_me(authorization: str | None = Header(None)) -> dict:
    store.delete_user(_me(authorization))
    return {"ok": True}


@router.post("/consent", summary="동의 기록 (어떤 동의를 언제 했는지만)")
def consent(body: ConsentRequest, authorization: str | None = Header(None)) -> dict:
    store.save_consent(_me(authorization), body.type, body.version)
    return {"ok": True}
