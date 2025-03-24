from fastapi import APIRouter, HTTPException, Query
from app.schemas.nutriologo import NutriologoCreate
from app.core.security import verify_invite_token
from app.services.user_service import create_nutriologo
from app.core.database import db

router = APIRouter(prefix="/nutriologo", tags=["Nutriólogo"])

@router.post("/register")
async def register_nutriologo(
    data: NutriologoCreate, token: str = Query(...)
):
    try:
        verify_invite_token(token)
    except:
        raise HTTPException(status_code=400, detail="Token inválido o expirado")
    
    existing_user = await db.usuarios.find_one({"email": data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    return await create_nutriologo(data.dict())
