from fastapi import APIRouter, Header, HTTPException
from core.security import create_invite_token
from core.config import settings

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/generate-invite")
def generate_invite(authorization: str = Header(...)):
    if authorization != f"Bearer {settings.ADMIN_TOKEN}":
        raise HTTPException(status_code=401, detail="No autorizado")
    token = create_invite_token("nutriologo")
    link = f"https://tu-dominio.onrender.com/register-nutriologo?token={token}" 
    return {"invite_link": link}
