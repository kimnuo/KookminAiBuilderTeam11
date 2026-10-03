"""가입·로그인. 화면(Flutter)의 닉네임 + 비밀번호 흐름에 맞춘다.

- 비밀번호는 scrypt(표준 라이브러리, 메모리를 많이 쓰는 비밀번호 전용 해시)로만 저장한다 (지침서 8절)
- 토큰은 난수. 세션 표에 두고 Authorization: Bearer <토큰> 으로 확인한다
- 이름·연락처·학번은 받지도 저장하지도 않는다. 닉네임만 받는다
"""

import hashlib
import secrets

from app.core.schemas import AuthResult
from app.db import store

NICKNAME_MIN, NICKNAME_MAX = 2, 12
PASSWORD_MIN = 8
_SCRYPT = {"n": 2**14, "r": 8, "p": 1}


class AuthError(Exception):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status
        self.message = message


def check_rules(nickname: str, password: str) -> None:
    if not NICKNAME_MIN <= len(nickname.strip()) <= NICKNAME_MAX:
        raise AuthError(400, f"닉네임은 {NICKNAME_MIN}~{NICKNAME_MAX}자로 적어 주세요.")
    letters = any(c.isalpha() for c in password)
    digits = any(c.isdigit() for c in password)
    if len(password) < PASSWORD_MIN or not letters or not digits:
        raise AuthError(400, f"비밀번호는 {PASSWORD_MIN}자 이상, 영문과 숫자를 섞어 주세요.")


def hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    key = hashlib.scrypt(password.encode("utf-8"), salt=salt, dklen=32, **_SCRYPT)
    return f"scrypt${salt.hex()}${key.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        kind, salt_hex, key_hex = stored.split("$")
    except ValueError:
        return False
    if kind != "scrypt":
        return False
    return secrets.compare_digest(hash_password(password, bytes.fromhex(salt_hex)), stored)


def signup(nickname: str, password: str) -> AuthResult:
    nickname = nickname.strip()
    check_rules(nickname, password)
    user_id = f"u_{secrets.token_hex(8)}"
    if not store.create_user(user_id, nickname, hash_password(password)):
        raise AuthError(409, "이미 쓰고 있는 닉네임이에요.")
    return AuthResult(id=user_id, token=_new_token(user_id))


def login(nickname: str, password: str) -> AuthResult:
    user = store.find_user(nickname.strip())
    if not user or not verify_password(password, user[1]):
        raise AuthError(401, "닉네임 또는 비밀번호가 맞지 않아요.")
    return AuthResult(id=user[0], token=_new_token(user[0]))


def _new_token(user_id: str) -> str:
    token = secrets.token_urlsafe(32)
    store.save_session(token, user_id)
    return token


def user_of(token: str | None) -> str | None:
    return store.session_user(token) if token else None
