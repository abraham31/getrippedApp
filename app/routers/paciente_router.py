from datetime import date, datetime, timedelta
import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Path, Response
from app.dependencies import get_current_user, require_role
from app.schemas.notificacion import NotificacionResponse
from app.schemas.paciente import CumplimientoCreate, CumplimientoSemana, DiaCumplido, PacienteActivate, SeleccionesPaciente
from app.schemas.notificacion import NotificacionResponse
from app.schemas.planalimenticio import PlanAlimenticio
from app.services.paciente_service import activate_paciente, generar_resumen_visual, generar_imagen_con_resumen_semanal, generar_imagen_con_progreso, generar_resumen_visual_semana
from bson import ObjectId
from app.core.database import db

router = APIRouter(prefix="/paciente", tags=["Paciente (App)"])

@router.post("/activar-paciente")
async def activar_cuenta(token: str, data: PacienteActivate):
    result = await activate_paciente(token, data.password)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.get("/notificaciones", response_model=List[NotificacionResponse])
async def listar_notificaciones(current_user: dict = Depends(get_current_user)):
    await require_role("paciente", current_user)

    notificaciones_cursor = db.notificaciones.find({
        "paciente_id": ObjectId(current_user["sub"])
    }, sort=[("fecha", -1)])

    notificaciones = []
    async for n in notificaciones_cursor:
        notificaciones.append({
            "id": str(n["_id"]),
            "titulo": n["titulo"],
            "mensaje": n["mensaje"],
            "fecha": n["fecha"],
            "leido": n["leido"],
            "tipo": n.get("tipo", "otro")
        })

    return notificaciones

@router.get("/notificaciones/{notificacion_id}/imagen")
async def generar_imagen_notificacion(
    notificacion_id: str,
    current_user: dict = Depends(get_current_user)
):
    await require_role("paciente", current_user)

    noti = await db.notificaciones.find_one({
        "_id": ObjectId(notificacion_id),
        "paciente_id": ObjectId(current_user["sub"])
    })

    if not noti:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")

    paciente = await db.usuarios.find_one({"_id": ObjectId(current_user["sub"])})
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    tipo = noti.get("tipo")

    if tipo == "progreso":
        if "consulta_id" not in noti:
            raise HTTPException(status_code=400, detail="Consulta no asociada")

        consulta = await db.consultas.find_one({"_id": noti["consulta_id"]})
        if not consulta:
            raise HTTPException(status_code=404, detail="Consulta no encontrada")

        progreso = consulta.get("progreso")
        if not progreso:
            raise HTTPException(status_code=400, detail="Progreso no registrado")

        consultas_previas = await db.consultas.find({
            "paciente_id": ObjectId(current_user["sub"]),
            "_id": {"$ne": consulta["_id"]}
        }).sort("fecha", -1).to_list(length=1)

        if not consultas_previas:
            raise HTTPException(status_code=400, detail="Se requiere al menos dos consultas para generar imagen")

        anterior = consultas_previas[0].get("progreso")
        resumen = generar_resumen_visual(progreso, anterior)

        nutriologo = await db.usuarios.find_one({"_id": consulta["nutriologo_id"]})
        image_bytes = generar_imagen_con_progreso(
            nombre_paciente=paciente["nombre"],
            nombre_nutriologo=nutriologo["nombre"],
            resumen=resumen
        )

    elif tipo == "resumen_semana":
        resumen = noti.get("resumen", [])
        if not resumen:
            raise HTTPException(status_code=400, detail="No hay resumen semanal registrado")

        nutriologo = await db.usuarios.find_one({"_id": noti.get("nutriologo_id")})
        if not nutriologo:
            raise HTTPException(status_code=404, detail="Nutriólogo no encontrado")

        image_bytes = generar_imagen_con_resumen_semanal(
            nombre_paciente=paciente["nombre"],
            nombre_nutriologo=nutriologo["nombre"],
            resumen=resumen
        )

    else:
        raise HTTPException(status_code=400, detail="Este tipo de notificación no soporta imagen")

    return Response(content=image_bytes, media_type="image/png")

@router.get("/paciente/plan", response_model=PlanAlimenticio)
async def obtener_plan_actual_paciente(current_user: dict = Depends(get_current_user)):
    await require_role("paciente", current_user)

    # Buscar la consulta más reciente del paciente que tenga un plan asignado
    consulta = await db.consultas.find_one(
        {
            "paciente_id": ObjectId(current_user["sub"]),
            "plan_id": {"$exists": True}
        },
        sort=[("fecha", -1)]
    )

    if not consulta:
        raise HTTPException(status_code=404, detail="No se encontró un plan alimenticio asignado")

    plan = await db.planes.find_one({"_id": consulta["plan_id"]})
    if not plan:
        raise HTTPException(status_code=404, detail="El plan alimenticio no fue encontrado")

    return plan

@router.post("/pacientes/{paciente_id}/resumen-semanal")
async def generar_resumen_semanal(
    paciente_id: str = Path(..., description="ID del paciente"),
    current_user: dict = Depends(get_current_user)
):
    await require_role("nutriologo", current_user)

    # Verifica que el paciente pertenezca al nutriólogo
    paciente = await db.usuarios.find_one({
        "_id": ObjectId(paciente_id),
        "nutriologo_id": current_user["sub"],
        "role": "paciente"
    })
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    # Buscar el cumplimiento de la semana más reciente (últimos 7 días)
    siete_dias_atras = datetime.utcnow() - timedelta(days=7)
    registros = await db.cumplimiento.find({
        "paciente_id": ObjectId(paciente_id),
        "fecha": {"$gte": siete_dias_atras}
    }).to_list(length=None)

    total_comidas = 0
    comidas_cumplidas = 0

    for registro in registros:
        for comida, cumplido in registro["cumplimiento"].items():
            total_comidas += 1
            if cumplido:
                comidas_cumplidas += 1

    if total_comidas == 0:
        raise HTTPException(status_code=400, detail="No hay registros de cumplimiento esta semana")

    porcentaje = round((comidas_cumplidas / total_comidas) * 100)

    # Generar resumen visual en formato lista
    resumen = generar_resumen_visual_semana({
        "total_comidas": total_comidas,
        "comidas_cumplidas": comidas_cumplidas
    })

    # Crear la notificación con el resumen y tipo
    await db.notificaciones.insert_one({
        "paciente_id": ObjectId(paciente_id),
        "titulo": "Resumen semanal de cumplimiento",
        "mensaje": resumen[-1],  # El mensaje motivacional final
        "fecha": datetime.utcnow(),
        "leido": False,
        "tipo": "resumen_semanal",
        "resumen": resumen,
        "nutriologo_id": ObjectId(current_user["sub"])
    })

    return {
        "msg": "Resumen semanal generado exitosamente",
        "porcentaje": porcentaje,
        "comidas_cumplidas": comidas_cumplidas,
        "total_comidas": total_comidas
    }

@router.get("/notificaciones/{notificacion_id}")
async def detalle_notificacion(
    notificacion_id: str,
    current_user: dict = Depends(get_current_user)
):
    await require_role("paciente", current_user)

    noti = await db.notificaciones.find_one({
        "_id": ObjectId(notificacion_id),
        "paciente_id": ObjectId(current_user["sub"])
    })

    if not noti:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")

    # Marcar como leída
    await db.notificaciones.update_one(
        {"_id": noti["_id"]},
        {"$set": {"leido": True}}
    )

    detalle = {
        "id": str(noti["_id"]),
        "tipo": noti.get("tipo", "otro"),
        "titulo": noti["titulo"],
        "mensaje": noti["mensaje"],
        "fecha": noti["fecha"],
        "leido": True,
        "puede_generar_imagen": False,
    }

    # Si la notificación incluye progreso
    if noti.get("tipo") == "progreso" and "consulta_id" in noti:
        consulta = await db.consultas.find_one({"_id": noti["consulta_id"]})
        if consulta and consulta.get("progreso"):
            detalle["progreso"] = consulta["progreso"]
            detalle["puede_generar_imagen"] = True

    elif noti.get("tipo") == "resumen_semana":
        detalle["puede_generar_imagen"] = True

    return detalle

@router.put("/plan/{plan_id}/selecciones")
async def seleccionar_ingredientes_plan(
    plan_id: str = Path(...),
    data: SeleccionesPaciente = ...,
    current_user: dict = Depends(get_current_user)
):
    await require_role("paciente", current_user)

    plan = await db.planes.find_one({"_id": ObjectId(plan_id)})
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")

    # Verificar que el plan esté vinculado a una consulta del paciente
    consulta = await db.consultas.find_one({
        "plan_id": ObjectId(plan_id),
        "paciente_id": ObjectId(current_user["sub"])
    })
    if not consulta:
        raise HTTPException(status_code=403, detail="No autorizado para modificar este plan")

    actualizado = False
    for sel in data.selecciones:
        for dia in plan["dias"]:
            if dia["nombre"] != sel.dia:
                continue
            for comida in dia["comidas"]:
                if comida["nombre"] != sel.comida:
                    continue
                for ingrediente in comida["ingredientes"]:
                    if ingrediente["nombre"] == sel.ingrediente and "alternativas" in ingrediente:
                        ingrediente["seleccionado"] = sel.seleccionado
                        actualizado = True

    if not actualizado:
        raise HTTPException(status_code=400, detail="No se encontró ningún ingrediente para actualizar")

    await db.planes.update_one(
        {"_id": ObjectId(plan_id)},
        {"$set": {"dias": plan["dias"]}}
    )

    return {"msg": "Selecciones guardadas correctamente"}

@router.post("/paciente/orden-compra")
async def generar_orden_compra(current_user: dict = Depends(get_current_user)):
    await require_role("paciente", current_user)

    paciente_id = ObjectId(current_user["sub"])

    # Buscar consulta más reciente con plan
    consulta = await db.consultas.find_one(
        {"paciente_id": paciente_id, "plan_id": {"$exists": True}},
        sort=[("fecha", -1)]
    )
    if not consulta:
        raise HTTPException(status_code=404, detail="No se encontró una consulta con plan asignado")

    plan = await db.planes.find_one({"_id": consulta["plan_id"]})
    if not plan:
        raise HTTPException(status_code=404, detail="Plan alimenticio no encontrado")

    ingredientes_totales = {}
    productos_tienda = []

    for dia in plan["dias"]:
        for comida in dia["comidas"]:
            for ing in comida["ingredientes"]:
                seleccionado = ing.get("seleccionado") or ing  # Puede ser alternativo o principal
                nombre = seleccionado["nombre"]
                cantidad = seleccionado["cantidad"]

                if seleccionado.get("producto_id"):
                    # Producto de tienda
                    producto = await db.productos.find_one({"_id": ObjectId(seleccionado["producto_id"])})
                    if producto:
                        productos_tienda.append({
                            "nombre": producto["nombre"],
                            "precio": producto["precio"],
                            "shopify_variant_id": producto.get("shopify_variant_id")
                        })
                    continue

                # Agrupar ingredientes por nombre
                if nombre not in ingredientes_totales:
                    ingredientes_totales[nombre] = cantidad
                else:
                    # Agrupación simple por texto; mejorable con normalización
                    ingredientes_totales[nombre] += f" + {cantidad}"

    # Precio base por semana (según número de comidas)
    comidas_por_dia = [len(d["comidas"]) for d in plan["dias"]]
    promedio = round(sum(comidas_por_dia) / len(comidas_por_dia))

    if promedio <= 6:
        precio_base = int(os.getenv("PRECIO_PLAN_SEMANA_6_COMIDAS", 800))
    elif promedio <= 8:
        precio_base = int(os.getenv("PRECIO_PLAN_SEMANA_8_COMIDAS", 1000))
    else:
        precio_base = int(os.getenv("PRECIO_PLAN_SEMANA_10_COMIDAS", 1200))

    total_productos_tienda = sum(p["precio"] for p in productos_tienda)
    precio_total = precio_base + total_productos_tienda

    # Guardar orden
    orden = {
        "paciente_id": paciente_id,
        "plan_id": consulta["plan_id"],
        "productos_mandado": [
            {"nombre": nombre, "cantidad_total": cantidad}
            for nombre, cantidad in ingredientes_totales.items()
        ],
        "productos_tienda": productos_tienda,
        "precio_base": precio_base,
        "precio_total": precio_total,
        "fecha": datetime.utcnow()
    }

    result = await db.ordenes.insert_one(orden)

    return {
        "msg": "Orden generada correctamente",
        "orden_id": str(result.inserted_id),
        "productos_mandado": orden["productos_mandado"],
        "productos_tienda": productos_tienda,
        "precio_base": precio_base,
        "precio_total": precio_total
    }

@router.get("/paciente/orden-compra")
async def obtener_ultima_orden_compra(current_user: dict = Depends(get_current_user)):
    await require_role("paciente", current_user)

    orden = await db.ordenes_compra.find_one(
        {"paciente_id": ObjectId(current_user["sub"])},
        sort=[("fecha", -1)]
    )

    if not orden:
        raise HTTPException(status_code=404, detail="No hay órdenes de compra registradas")

    return {
        "fecha": orden["fecha"],
        "total": orden["total"],
        "productos_tienda": [
            {"nombre": p["nombre"], "precio": p["precio"]}
            for p in orden.get("productos_tienda", [])
        ],
        "incluye_servicio_comidas": orden.get("incluye_servicio_comidas", True),
        "resumen": orden["resumen"]
    }

@router.get("/paciente/orden-compra/shopify-url")
async def generar_url_shopify(current_user: dict = Depends(get_current_user)):
    await require_role("paciente", current_user)

    paciente_id = ObjectId(current_user["sub"])

    orden = await db.ordenes.find_one(
        {"paciente_id": paciente_id},
        sort=[("fecha", -1)]
    )

    if not orden:
        raise HTTPException(status_code=404, detail="No se encontró una orden de compra reciente")

    items = []

    # Cargar precios desde variables de entorno
    precio_6 = int(os.getenv("PRECIO_PLAN_6_COMIDAS", 800))
    precio_8 = int(os.getenv("PRECIO_PLAN_8_COMIDAS", 1000))
    precio_10 = int(os.getenv("PRECIO_PLAN_10_COMIDAS", 1200))

    # Asociar precio base con producto de Shopify
    base_id = None
    if orden["precio_base"] == precio_6:
        base_id = os.getenv("PRODUCTO_SHOPIFY_6_COMIDAS")
    elif orden["precio_base"] == precio_8:
        base_id = os.getenv("PRODUCTO_SHOPIFY_8_COMIDAS")
    elif orden["precio_base"] == precio_10:
        base_id = os.getenv("PRODUCTO_SHOPIFY_10_COMIDAS")

    if base_id:
        items.append(f"{base_id}:1")

    # Productos de tienda adicionales
    for prod in orden.get("productos_tienda", []):
        shopify_id = prod.get("shopify_variant_id")
        if shopify_id:
            items.append(f"{shopify_id}:1")

    if not items:
        raise HTTPException(status_code=400, detail="La orden no contiene productos con ID de Shopify")

    base_url = os.getenv("SHOPIFY_BASE_URL", "https://getripped.myshopify.com/cart")
    url = f"{base_url}/{'/'.join(items)}"

    return {"url": url}








