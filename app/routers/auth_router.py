from fastapi import APIRouter, HTTPException
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.user_service import authenticate_user
from app.core.database import db

router = APIRouter(tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest):
    token = await authenticate_user(data.email, data.password)
    if not token:
        raise HTTPException(status_code=400, detail="Credenciales inválidas")
    return {"access_token": token}
