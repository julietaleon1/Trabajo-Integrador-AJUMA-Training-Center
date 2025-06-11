from fastapi import FastAPI, Request
import json
from datetime import datetime
import os
import requests

app = FastAPI()
MP_ACCESS_TOKEN = "APP_USR-4854110216283719-060421-2ed2ca1bb7d75a488b6629740499297c-189553208"

def obtener_pago_mp(payment_id):
    url = f"https://api.mercadopago.com/v1/payments/{payment_id}"
    headers = {
        "Authorization": f"Bearer {MP_ACCESS_TOKEN}"
    }
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        return resp.json()
    return None

@app.post("/webhook")
async def mercadopago_webhook(request: Request):
    body = await request.json()
    try:
        payment_id = None
        if "data" in body and isinstance(body["data"], dict):
            payment_id = body["data"].get("id") or body["data"].get("payment_id")
        elif "data.id" in body:
            payment_id = body.get("data.id")
        if payment_id:
            pago = obtener_pago_mp(payment_id)
            if pago:
                fecha_pago = pago.get("date_created", datetime.now().strftime("%Y-%m-%d"))
                monto = pago.get("transaction_amount", 0)
                descripcion = pago.get("description", "")
                id_pago_mp = pago.get("id")
                cliente_id = pago.get("metadata", {}).get("cliente_id")
                if cliente_id:
                    actualizar_cliente_pago_por_id(cliente_id, fecha_pago[:10], monto, descripcion, id_pago_mp)
    except Exception as e:
        print(f"Error actualizando cliente: {e}")
    return {"status": "ok"}

def actualizar_cliente_pago_por_id(cliente_id, fecha_pago, monto=0, descripcion="", id_pago_mp=None):
    CLIENTES_FILE = "./clientes.json"
    if not os.path.exists(CLIENTES_FILE):
        return
    with open(CLIENTES_FILE, "r", encoding="utf-8") as f:
        clientes = json.load(f)
    for c in clientes:
        if str(c.get("id")) == str(cliente_id):
            if "facturacion" not in c or not isinstance(c["facturacion"], list):
                c["facturacion"] = []
            nuevo_pago = {
                "fecha_pago": fecha_pago,
                "monto": monto,
                "descripcion": descripcion,
                "estado": "Pagado",
                "id_pago_mp": id_pago_mp
            }
            c["facturacion"].append(nuevo_pago)
            c["fecha_ingreso"] = fecha_pago
    with open(CLIENTES_FILE, "w", encoding="utf-8") as f:
        json.dump(clientes, f, ensure_ascii=False, indent=4)