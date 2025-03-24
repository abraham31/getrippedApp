from fastapi import APIRouter, Depends, HTTPException
from app.core.security import create_invite_token
from app.core.config import settings
from app.dependencies import get_current_user, require_role

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/generate-invite")
async def generate_invite(current_user: dict = Depends(get_current_user)):
    # Solo permitir admins
    await require_role("admin", current_user)
    
    # Generar token de invitación
    token = create_invite_token("nutriologo")
    
    # Construir link dinámico
    link = f"{settings.APP_URL}/nutriologo/activate?token={token}"
    
    return {"invite_link": link}


