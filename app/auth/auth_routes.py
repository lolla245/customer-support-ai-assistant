# auth_routes.py
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
import sys, os

sys.path.append(os.path.dirname(__file__))
from security import get_user, create_user, verify_password, create_access_token, decode_access_token

auth_router = APIRouter(prefix="/auth")


class SignupRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


@auth_router.post("/signup")
async def signup(request: SignupRequest):
    if len(request.username.strip()) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters")
    if len(request.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    user = create_user(request.username.strip(), request.password)
    if user is None:
        raise HTTPException(status_code=400, detail="Username already exists")

    token = create_access_token(request.username.strip())
    return {"status": "success", "access_token": token, "token_type": "bearer"}


@auth_router.post("/login")
async def login(request: LoginRequest):
    user = get_user(request.username.strip())
    if not user or not verify_password(request.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token(request.username.strip())
    return {"status": "success", "access_token": token, "token_type": "bearer"}


@auth_router.get("/me")
async def get_me(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization.replace("Bearer ", "")
    username = decode_access_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return {"username": username}