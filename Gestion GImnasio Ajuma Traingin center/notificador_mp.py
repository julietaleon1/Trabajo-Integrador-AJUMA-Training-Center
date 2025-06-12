from fastapi import FastAPI, Request  # Importa FastAPI y el objeto Request para manejar solicitudes HTTP
import json  # Para trabajar con archivos JSON
from datetime import datetime  # Para obtener la fecha actual
import os  # Para verificar existencia de archivos
import requests  # Para hacer solicitudes HTTP (al API de MercadoPago)

app = FastAPI()  # Crea la aplicación FastAPI

# Token de acceso a la cuenta de MercadoPago (debería protegerse en entorno real)
MP_ACCESS_TOKEN = "APP_USR-4854110216283719-060421-2ed2ca1bb7d75a488b6629740499297c-189553208"

# === FUNCIÓN PARA OBTENER INFORMACIÓN DETALLADA DE UN PAGO EN MERCADOPAGO ===
def obtener_pago_mp(payment_id):
    url = f"https://api.mercadopago.com/v1/payments/{payment_id}"  # Endpoint de MercadoPago para consultar un pago
    headers = {
        "Authorization": f"Bearer {MP_ACCESS_TOKEN}"  # Token de autorización
    }
    resp = requests.get(url, headers=headers)  # Hace la solicitud GET a la API
    if resp.status_code == 200:
        return resp.json()  # Si fue exitoso, devuelve los datos del pago como diccionario
    return None  # Si hubo un error, devuelve None

# === ENDPOINT DE WEBHOOK PARA RECIBIR NOTIFICACIONES DE PAGO DE MERCADOPAGO ===
@app.post("/webhook")
async def mercadopago_webhook(request: Request):
    body = await request.json()  # Lee el cuerpo de la solicitud como JSON
    try:
        payment_id = None

        # Intenta obtener el ID del pago de varias formas posibles
        if "data" in body and isinstance(body["data"], dict):
            payment_id = body["data"].get("id") or body["data"].get("payment_id")
        elif "data.id" in body:
            payment_id = body.get("data.id")

        # Si se obtuvo un payment_id, se busca el detalle del pago
        if payment_id:
            pago = obtener_pago_mp(payment_id)  # Consulta los datos del pago a MercadoPago

            if pago:
                fecha_pago = pago.get("date_created", datetime.now().strftime("%Y-%m-%d"))  # Fecha del pago
                monto = pago.get("transaction_amount", 0)  # Monto del pago
                descripcion = pago.get("description", "")  # Descripción del pago
                id_pago_mp = pago.get("id")  # ID del pago en MercadoPago
                cliente_id = pago.get("metadata", {}).get("cliente_id")  # ID del cliente (si se envió en metadata)

                # Si se encuentra el cliente, se actualiza su información de pago en el archivo JSON
                if cliente_id:
                    actualizar_cliente_pago_por_id(cliente_id, fecha_pago[:10], monto, descripcion, id_pago_mp)
    except Exception as e:
        print(f"Error actualizando cliente: {e}")  # Muestra error si algo sale mal

    return {"status": "ok"}  # Devuelve una respuesta simple para confirmar recepción

# === ACTUALIZA EL ARCHIVO JSON DE CLIENTES CON EL NUEVO PAGO ===
def actualizar_cliente_pago_por_id(cliente_id, fecha_pago, monto=0, descripcion="", id_pago_mp=None):
    CLIENTES_FILE = "./clientes.json"  # Ruta al archivo de clientes

    # Si el archivo no existe, termina la función
    if not os.path.exists(CLIENTES_FILE):
        return

    # Abre y carga el archivo JSON con los datos actuales
    with open(CLIENTES_FILE, "r", encoding="utf-8") as f:
        clientes = json.load(f)

    # Recorre todos los clientes
    for c in clientes:
        if str(c.get("id")) == str(cliente_id):  # Busca el cliente por ID
            if "facturacion" not in c or not isinstance(c["facturacion"], list):
                c["facturacion"] = []  # Si no tiene historial de facturación, lo crea

            # Crea un nuevo registro de pago
            nuevo_pago = {
                "fecha_pago": fecha_pago,
                "monto": monto,
                "descripcion": descripcion,
                "estado": "Pagado",
                "id_pago_mp": id_pago_mp
            }

            # Agrega el nuevo pago a la lista de facturación
            c["facturacion"].append(nuevo_pago)

            # Actualiza también la fecha de ingreso del cliente
            c["fecha_ingreso"] = fecha_pago

    # Guarda nuevamente el archivo con los cambios
    with open(CLIENTES_FILE, "w", encoding="utf-8") as f:
        json.dump(clientes, f, ensure_ascii=False, indent=4)
