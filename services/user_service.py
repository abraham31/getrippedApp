from core.database import db
from core.security import hash_password, verify_password, create_access_token

async def create_nutriologo(data: dict):
    user = {
        "nombre": data["nombre"],
        "email": data["email"],
        "password": hash_password(data["password"]),
        "curp": data["curp"],
        "role": "nutriologo"
    }
    await db.usuarios.insert_one(user)
    return {"msg": "Nutriólogo creado correctamente"}

async def authenticate_user(email: str, password: str):
    user = await db.usuarios.find_one({"email": email})
    if not user:
        return None
    if not verify_password(password, user["password"]):
        return None
    token_data = {
        "sub": str(user["_id"]),
        "role": user["role"]
    }
    token = create_access_token(token_data)
    return token
