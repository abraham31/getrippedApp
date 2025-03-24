from fastapi import APIRouter, Header, HTTPException
from app.core.security import create_invite_token
from app.core.config import settings

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/generate-invite")
def generate_invite(authorization: str = Header(...)):
    if authorization != f"Bearer {settings.ADMIN_TOKEN}":
        raise HTTPException(status_code=401, detail="No autorizado")
    
    # Generamos token para el nutriólogo
    token = create_invite_token("nutriologo")
    
    # Construimos link dinámico con APP_URL desde settings
    link = f"{settings.APP_URL}/register-nutriologo?token={token}"
    
    return {"invite_link": link}

