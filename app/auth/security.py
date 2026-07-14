# security.py
import os
import json
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt

SECRET_KEY = os.getenv("JWT_SECRET", "change-this-secret-in-env")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")


def _load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)


def _save_users(users: dict):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def get_user(username: str):
    users = _load_users()
    return users.get(username)


def create_user(username: str, password: str):
    users = _load_users()
    if username in users:
        return None  # already exists
    users[username] = {
        "username": username,
        "hashed_password": pwd_context.hash(password),
        "created_at": datetime.utcnow().isoformat()
    }
    _save_users(users)
    return users[username]


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(username: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": username, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None