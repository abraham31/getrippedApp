from datetime import datetime, date
import io, textwrap
from app.core.database import db
from app.core.security import create_activation_token, verify_activation_token, hash_password
from app.services.email_service import send_activation_email
from bson import ObjectId
from PIL import Image, ImageDraw, ImageFont

async def crear_paciente(data: dict, nutriologo_id: str):
    existing = await db.usuarios.find_one({"email": data["email"]})
    if existing:
        return {"error": "Email ya registrado"}

    paciente = data.copy()

    if isinstance(paciente.get("fecha_nacimiento"), date):
        paciente["fecha_nacimiento"] = datetime.combine(paciente["fecha_nacimiento"], datetime.min.time())
    
    paciente.update({
        "nutriologo_id": nutriologo_id,
        "role": "paciente",
        "is_active": False,
        "is_deleted": False,
        "password": None
    })

    result = await db.usuarios.insert_one(paciente)

    activation_token = create_activation_token(str(result.inserted_id))

    try:
        send_activation_email(data["email"], activation_token)
    except:
        return {"error": "Error enviando email"}

    return {
        "msg": "Paciente creado, email enviado.",
        "activation_token": activation_token
    }

async def activate_paciente(token: str, password: str):
    try:
        payload = verify_activation_token(token)
        paciente_id = payload.get("user_id")
        if not paciente_id:
            return {"error": "Token inválido"}
    except:
        return {"error": "Token inválido o expirado"}

    paciente = await db.usuarios.find_one({
        "_id": ObjectId(paciente_id),
        "role": "paciente",
        "is_deleted": False
    })

    if not paciente:
        return {"error": "Paciente no encontrado"}

    if paciente.get("is_active"):
        return {"error": "Cuenta ya activada"}

    await db.usuarios.update_one(
        {"_id": ObjectId(paciente_id)},
        {
            "$set": {
                "password": hash_password(password),
                "is_active": True
            }
        }
    )
    return {"msg": "Cuenta activada correctamente"}

def generar_resumen_visual(actual: dict, anterior: dict | None) -> list[str]:
    if not anterior:
        return [
            "🎯 ¡Inicio registrado!",
            "Comienza tu camino de transformación. ¡Vamos con todo!"
        ]

    mensajes = []

    def comparar_clave(clave, texto_positivo, unidad="kg", emoji=""):
        if clave in actual and clave in anterior:
            dif = round(actual[clave] - anterior[clave], 2)
            if dif < 0:
                mensajes.append(f"{texto_positivo} {abs(dif)} {unidad} {emoji}")
            elif dif > 0 and clave == "masa_muscular":
                mensajes.append(f"Ganaste {dif} {unidad} de masa muscular 💪")

    comparar_clave("peso", "Bajaste", "kg", "📉")
    comparar_clave("masa_grasa", "Reduciste grasa corporal", "kg", "🔥")
    comparar_clave("porcentaje_grasa_corporal", "Bajaste grasa corporal (%)", "%", "🏆")

    if not mensajes:
        mensajes.append("¡Seguimos avanzando! A veces el cambio no se ve, pero cuenta 💪")

    return mensajes

def generar_resumen_visual_semana(porcentaje: float, total: int, cumplidas: int) -> list[str]:
    mensajes = [
        f"🍽️ Total de comidas esta semana: {total}",
        f"✅ Comidas cumplidas: {cumplidas}",
        f"📊 Cumplimiento: {porcentaje}%"
    ]

    if porcentaje >= 90:
        mensajes.append("¡Excelente semana! Tu compromiso es increíble 💪🔥")
    elif porcentaje >= 75:
        mensajes.append("¡Muy bien! Estás haciendo un gran esfuerzo 🥗👏")
    elif porcentaje >= 50:
        mensajes.append("Vamos por más la próxima semana 💥")
    else:
        mensajes.append("Lo importante es seguir intentando. ¡Tú puedes! 🚀")

    return mensajes

def generar_imagen_con_progreso(
    nombre_paciente: str,
    nombre_nutriologo: str,
    resumen: list[str],
    tipo: str = "progreso"
) -> bytes:
    width, height = 1080, 1920
    background_color = (255, 255, 255)

    image = Image.new("RGB", (width, height), background_color)
    draw = ImageDraw.Draw(image)

    try:
        title_font = ImageFont.truetype("arial.ttf", 80)
        subtitle_font = ImageFont.truetype("arial.ttf", 50)
        text_font = ImageFont.truetype("arial.ttf", 40)
    except:
        title_font = subtitle_font = text_font = ImageFont.load_default()

    y = 100
    padding = 80

    titulo = "🎯 ¡Progreso alcanzado!" if tipo == "progreso" else "📅 Resumen semanal"
    draw.text((padding, y), titulo, font=title_font, fill="black")
    y += 150

    draw.text((padding, y), f"{nombre_paciente}", font=subtitle_font, fill="black")
    y += 100

    for linea in resumen:
        wrapped = textwrap.wrap(linea, width=30)
        for l in wrapped:
            draw.text((padding, y), l, font=text_font, fill="black")
            y += 60
        y += 20

    branding = f"GetRippedApp / By {nombre_nutriologo}"
    draw.text((padding, height - 100), branding, font=text_font, fill="gray")

    output = io.BytesIO()
    image.save(output, format="PNG")
    output.seek(0)
    return output.read()
