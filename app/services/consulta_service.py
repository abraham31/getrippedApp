from datetime import datetime
from bson import ObjectId

def crear_consulta(paciente_id: str, nutriologo_id: str, data: dict, consultas_anteriores: list) -> dict:
    es_primera = len(consultas_anteriores) == 0
    progreso = data["progreso"]

    if es_primera:
        titulo = "¡Bienvenido a tu seguimiento!"
        mensaje = "Tu primera consulta ha sido registrada. A partir de ahora haremos seguimiento a tu evolución. 🎯"
        mensaje += _generar_resumen_inicial(progreso)
    else:
        anterior = consultas_anteriores[-1]["progreso"]
        mensajes = _comparar_progreso(progreso, anterior)

        if mensajes:
            titulo = "¡Felicidades por tu progreso!"
            mensaje = " ".join(mensajes)
        else:
            titulo = "¡Seguimos trabajando!"
            mensaje = "No hubo cambios significativos esta vez."

    return {
        "consulta": {
            "paciente_id": ObjectId(paciente_id),
            "nutriologo_id": ObjectId(nutriologo_id),
            "fecha": data.get("fecha") or datetime.utcnow().date(),
            "tipo": data.get("tipo"),
            "progreso": progreso,
            "observaciones": data.get("observaciones"),
            "notificacion_generada": True,
        },
        "notificacion": {
            "titulo": titulo,
            "mensaje": mensaje
        }
    }

def _generar_resumen_inicial(progreso: dict) -> str:
    resumen = []

    if progreso.get("peso"):
        resumen.append(f"Peso: {progreso['peso']} kg")
    if progreso.get("masa_muscular") is not None:
        resumen.append(f"Masa muscular: {progreso['masa_muscular']} kg")
    if progreso.get("masa_grasa") is not None:
        resumen.append(f"Masa grasa: {progreso['masa_grasa']} kg")
    if progreso.get("porcentaje_grasa_corporal") is not None:
        resumen.append(f"% grasa corporal: {progreso['porcentaje_grasa_corporal']}%")

    return "\n\n📝 Resultados iniciales:\n" + "\n".join(resumen) if resumen else ""

def _comparar_progreso(actual: dict, anterior: dict) -> list:
    mensajes = []

    if anterior.get("peso") and actual.get("peso"):
        dif = round(actual["peso"] - anterior["peso"], 2)
        if dif < 0:
            mensajes.append(f"Bajaste {abs(dif)} kg de peso.")
        elif dif > 0:
            mensajes.append(f"Subiste {dif} kg de peso.")

    if anterior.get("masa_muscular") and actual.get("masa_muscular"):
        dif = round(actual["masa_muscular"] - anterior["masa_muscular"], 2)
        if dif > 0:
            mensajes.append(f"Ganaste {dif} kg de masa muscular 💪.")

    if anterior.get("masa_grasa") and actual.get("masa_grasa"):
        dif = round(actual["masa_grasa"] - anterior["masa_grasa"], 2)
        if dif < 0:
            mensajes.append(f"Reduciste {abs(dif)} kg de grasa corporal 🔥.")

    if anterior.get("porcentaje_grasa_corporal") and actual.get("porcentaje_grasa_corporal"):
        dif = round(actual["porcentaje_grasa_corporal"] - anterior["porcentaje_grasa_corporal"], 2)
        if dif < 0:
            mensajes.append(f"Bajaste {abs(dif)}% de grasa corporal 🏆.")

    return mensajes

