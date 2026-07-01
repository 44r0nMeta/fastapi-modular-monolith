from __future__ import annotations

from fastapi import APIRouter, status

from app.core.dependencies import DBSession
from app.modules.auth.dependencies import CurrentUser
from app.modules.auth.schemas import (
    LoginRequest,
    RefreshRequest,
    TokenPair,
    UserCreate,
    UserRead,
)
from app.modules.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, session: DBSession) -> UserRead:
    user = await AuthService(session).register(data)
    return UserRead.model_validate(user)


@router.post("/login", response_model=TokenPair)
async def login(data: LoginRequest, session: DBSession) -> TokenPair:
    return await AuthService(session).login(data.email, data.password)


@router.post("/refresh", response_model=TokenPair)
async def refresh(data: RefreshRequest, session: DBSession) -> TokenPair:
    return await AuthService(session).refresh(data.refresh_token)


@router.get("/me", response_model=UserRead)
async def me(user: CurrentUser) -> UserRead:
    return UserRead.model_validate(user)
