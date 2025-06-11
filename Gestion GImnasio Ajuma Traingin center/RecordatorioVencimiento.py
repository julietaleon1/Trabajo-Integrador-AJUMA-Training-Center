import smtplib
import json
from datetime import datetime, timedelta
from email.message import EmailMessage
from email.utils import make_msgid
import os
import mercadopago

MP_ACCESS_TOKEN = "APP_USR-3725378194687616-060622-013c07d1a71e2e0a0c1518ed3f2c7b35-1126088577"
ARCHIVO_JSON_CLIENTES = 'clientes.json'
DIAS_ANTICIPACION_RECORDATORIO = 3
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 465

REMITENTE_EMAIL = "ajumatrainingcenter@gmail.com"
REMITENTE_PASSWORD = "uuqi sqqd ndig ttna"

def cargar_clientes(ruta_archivo):
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def calcular_fecha_vencimiento(fecha_ingreso, plan):
    if plan == "Mensual":
        return fecha_ingreso + timedelta(days=30)
    elif plan == "Trimestral":
        return fecha_ingreso + timedelta(days=90)
    elif plan == "Anual":
        return fecha_ingreso + timedelta(days=365)
    else:
        return fecha_ingreso
    
def crear_link_pago(nombre, email, monto, descripcion, cliente_id=None):
    sdk = mercadopago.SDK(MP_ACCESS_TOKEN)
    preference_data = {
        "items": [
            {
                "title": descripcion,
                "description": f"Pago de cuota para {nombre}",
                "quantity": 1,
                "currency_id": "ARS",
                "unit_price": monto
            }
        ],
        "payer": {
            "name": nombre,
            "email": email,
        },
        "back_urls": {
            "success": "https://www.example.com/success",
            "failure": "https://www.example.com/failure",
            "pending": "https://www.example.com/pending"
        },
        "auto_return": "approved",
        "metadata": {
            "cliente_id": cliente_id if cliente_id else None
        }
    }
    response = sdk.preference().create(preference_data)
    if response["status"] == 201:
        return response["response"]["init_point"]
    else:
        return None
    
def enviar_correo_recordatorio(destinatario_email, nombre_cliente, fecha_pago_str, remitente_email_local, remitente_password_local, link_pago):
    try:
        msg = EmailMessage()
        msg['Subject'] = f"📢 Recordatorio de Vencimiento de Cuota - {nombre_cliente}"
        msg['From'] = remitente_email_local
        msg['To'] = destinatario_email

        imagen_cid = make_msgid(domain='logo-ajuma.png')[1:-1]

        cuerpo_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #e0e0e0; margin: 0; padding: 0; background-color: #111111; }}
                .email-container {{ width: 100%; max-width: 600px; margin: 20px auto; background-color: #181818; border: 1px solid #222; border-radius: 10px; overflow: hidden; }}
                .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; }}
                .header h2 {{ margin: 0; }}
                .content {{ padding: 25px; text-align: left; color: #e0e0e0; }}
                .content p {{ margin-bottom: 15px; }}
                .highlight {{ color: #007bff; font-weight: bold; }}
                .button-link {{ display: inline-block; background-color: #007bff; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px; margin-top: 10px; }}
                .footer {{ background-color: #181818; padding: 20px; text-align: center; font-size: 0.9em; color: #888; border-top: 1px solid #222; }}
                .footer img {{ max-width: 200px; height: auto; margin-bottom: 10px; }}
                a {{ color: #007bff; }}
                a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <h2>Recordatorio de Pago Pendiente</h2>
                </div>
                <div class="content">
                    <p>Estimado/a <strong>{nombre_cliente}</strong>,</p>
                    <p>Este es un recordatorio amistoso de que su próxima cuota para Ajuma Training Center está programada para vencer el día <span class="highlight">{fecha_pago_str}</span>.</p>
                    <p>Para asegurar la continuidad de sus servicios y evitar cualquier inconveniente, le agradecemos realice el pago a tiempo.</p>
                    <p>Si ya ha realizado el pago, por favor ignore este mensaje. Si tiene alguna consulta o necesita asistencia, no dude en <a href="mailto:{remitente_email_local}?subject=Consulta%20sobre%20vencimiento%20de%20cuota">contactarnos</a>.</p>
                    <p><a href="{link_pago}" class="button-link">Realizar Pago Ahora</a></p>
                    <p>¡Gracias por ser parte de Ajuma Training Center!</p>
                </div>
                <div class="footer">
                    <img src="cid:{imagen_cid}" alt="Logo Ajuma Training Center">
                    <p><strong>El equipo de Ajuma Training Center</strong></p>
                    <p>Si no puedes ver la imagen, visita nuestro <a href="[ENLACE_A_TU_SITIO_WEB]">sitio web</a>.</p>
                </div>
            </div>
        </body>
        </html>
        """
        msg.set_content("Este es un recordatorio de que su próxima cuota vence pronto.")
        msg.add_alternative(cuerpo_html, subtype='html')

        logo_path = os.path.join(os.path.dirname(__file__), "logo-ajuma.png")
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as img:
                msg.get_payload()[1].add_related(
                    img.read(),
                    maintype='image',
                    subtype='png',
                    cid=f"<{imagen_cid}>"
                )

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.login(remitente_email_local, remitente_password_local)
            smtp.send_message(msg)
        print(f"Correo enviado a {destinatario_email}")
    except Exception as e:
        print(f"Error al enviar el correo a {destinatario_email}: {e}")

def obtener_ultima_fecha_pago(cliente):
    facturacion = cliente.get("facturacion", [])
    if not facturacion:
        return cliente.get("fecha_ingreso")
    fechas = [f.get("fecha_pago") for f in facturacion if f.get("fecha_pago")]
    if not fechas:
        return cliente.get("fecha_ingreso")
    return max(fechas)

def main():
    clientes = cargar_clientes(ARCHIVO_JSON_CLIENTES)
    hoy = datetime.now().date()
    for cliente in clientes:
        try:
            nombre = cliente.get("nombre", "")
            email = cliente.get("email", "")
            plan = cliente.get("plan", "")
            fecha_base_str = obtener_ultima_fecha_pago(cliente)
            if not (nombre and email and plan and fecha_base_str):
                continue
            fecha_base = datetime.strptime(fecha_base_str, "%Y-%m-%d").date()
            fecha_vencimiento = calcular_fecha_vencimiento(fecha_base, plan)
            dias_restantes = (fecha_vencimiento - hoy).days
            if 0 <= dias_restantes <= DIAS_ANTICIPACION_RECORDATORIO:
                monto = 10  # O el monto real según el plan
                descripcion = f"Cuota {plan} Ajuma Training Center"
                link_pago = crear_link_pago(nombre, email, monto, descripcion, cliente.get("id"))
                if link_pago:
                    enviar_correo_recordatorio(email, nombre, fecha_vencimiento.strftime("%Y-%m-%d"), REMITENTE_EMAIL, REMITENTE_PASSWORD, link_pago)
        except Exception as e:
            print(f"Error procesando cliente: {e}")

# Ejecutar solo si se corre directamente, no al importar
if __name__ == "__main__":
    main()
