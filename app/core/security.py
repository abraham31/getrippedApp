from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash de password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Token para invitación (ya teníamos esto)
def create_invite_token(role: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=settings.INVITE_TOKEN_EXPIRE_HOURS)
    to_encode = {"type": "invite", "role": role, "exp": expire}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")

def verify_invite_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        if payload.get("type") != "invite" or payload.get("role") != "nutriologo":
            raise JWTError("Invalid invite token")
        return payload
    except JWTError:
        raise

# ----------------------------
# NUEVO: Token para login
# ----------------------------
def create_access_token(data: dict, expires_minutes: int = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        raise JWTError("Token inválido o expirado")

# Token para activación de cuenta paciente
def create_activation_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=48)  # Expira en 48 hrs
    to_encode = {"type": "activate", "user_id": user_id, "exp": expire}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")

def verify_activation_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        if payload.get("type") != "activate":
            raise JWTError("Token inválido")
        return payload
    except JWTError:
        raise
