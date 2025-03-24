from fastapi import APIRouter, HTTPException, Query
from app.schemas.nutriologo import NutriologoCreate
from app.schemas.auth import LoginRequest, TokenResponse
from app.core.security import verify_invite_token
from app.services.user_service import create_nutriologo, authenticate_user
from app.core.database import db

router = APIRouter(tags=["Auth"])

@router.post("/register-nutriologo")
async def register_nutriologo(
    data: NutriologoCreate, token: str = Query(...)
):
    try:
        verify_invite_token(token)
    except:
        raise HTTPException(status_code=400, detail="Token inválido o expirado, solicite uno nuevo")
    
    existing_user = await db.usuarios.find_one({"email": data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    return await create_nutriologo(data.dict())

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest):
    token = await authenticate_user(data.email, data.password)
    if not token:
        raise HTTPException(status_code=400, detail="Credenciales inválidas")
    return {"access_token": token}
