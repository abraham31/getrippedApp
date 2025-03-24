from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_access_token(token)
        return payload
    except:
        raise HTTPException(status_code=401, detail="Token inválido")

async def require_role(required_role: str, user: dict = Depends(get_current_user)):
    if user["role"] != required_role:
        raise HTTPException(status_code=403, detail="Acceso denegado")
