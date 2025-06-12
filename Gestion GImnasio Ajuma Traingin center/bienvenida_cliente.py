import mercadopago  # SDK de MercadoPago para generar links de pago
import smtplib  # Librería estándar para enviar correos con SMTP
from email.message import EmailMessage  # Clase para construir emails

# === CREDENCIALES Y CONFIGURACIÓN ===
MP_ACCESS_TOKEN = "APP_USR-3725378194687616-060622-013c07d1a71e2e0a0c1518ed3f2c7b35-1126088577"  # Token de acceso a tu cuenta de MercadoPago
SMTP_SERVER = 'smtp.gmail.com'  # Servidor SMTP de Gmail
SMTP_PORT = 465  # Puerto para SMTP con SSL
REMITENTE_EMAIL = "ajumatrainingcenter@gmail.com"  # Dirección de correo que envía los emails
REMITENTE_PASSWORD = "uuqi sqqd ndig ttna"  # Contraseña de aplicación para Gmail (no es la contraseña de la cuenta)

# === FUNCIÓN PARA GENERAR UN LINK DE PAGO EN MERCADOPAGO ===
def crear_link_pago(nombre, email, monto, descripcion, cliente_id=None):
    sdk = mercadopago.SDK(MP_ACCESS_TOKEN)  # Se instancia el objeto SDK con tu token de acceso
    preference_data = {
        "items": [
            {
                "title": descripcion,  # Título del producto o servicio
                "description": f"Pago de cuota para {nombre}",  # Descripción más detallada
                "quantity": 1,  # Siempre es 1 cuota
                "currency_id": "ARS",  # Moneda en Pesos Argentinos
                "unit_price": monto  # Monto a cobrar
            }
        ],
        "payer": {
            "name": nombre,  # Nombre del cliente
            "email": email,  # Email del cliente
        },
        "back_urls": {  # URLs a las que redirige según el estado del pago
            "success": "https://1h6gztrs-8000.brs.devtunnels.ms/success",
            "failure": "https://www.example.com/failure",
            "pending": "https://www.example.com/pending"
        },
        "auto_return": "approved",  # Redirige automáticamente al success si el pago fue aprobado
        "metadata": {
            "cliente_id": cliente_id if cliente_id else None  # Info adicional útil para identificar al cliente internamente
        }
    }
    response = sdk.preference().create(preference_data)  # Se crea la preferencia (link de pago)
    if response["status"] == 201:
        return response["response"]["init_point"]  # Se retorna el link al que el cliente debe ingresar para pagar
    else:
        return None  # Si hubo un error, se retorna None

# === FUNCIÓN PARA ENVIAR EMAIL DE BIENVENIDA CON EL LINK DE PAGO ===
def enviar_bienvenida(nombre, email, plan, cliente_id):
    # Se define el monto según el plan elegido
    monto = 10 if plan == "Mensual" else 11 if plan == "Trimestral" else 12
    descripcion = f"Cuota {plan} Ajuma Training Center"  # Descripción visible en MercadoPago
    link_pago = crear_link_pago(nombre, email, monto, descripcion, cliente_id)  # Se genera el link de pago

    if not link_pago:
        return False  # Si no se pudo generar el link, se sale de la función

    # Se construye el mensaje de correo
    msg = EmailMessage()
    msg['Subject'] = f"¡Bienvenido/a a Ajuma Training Center, {nombre}!"  # Asunto del email
    msg['From'] = REMITENTE_EMAIL  # Remitente
    msg['To'] = email  # Destinatario

    # Contenido en texto plano como alternativa de respaldo
    msg.set_content("Bienvenido/a a Ajuma Training Center. Realice su pago aquí: " + link_pago)

    # Contenido en HTML más atractivo visualmente
    cuerpo_html = f"""
    <html>
     <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #e0e0e0; margin: 0; padding: 0; background-color: #111111;}}
                .email-container {{ width: 100%; max-width: 600px; margin: 20px auto; background-color: #181818; border: 1px solid #222; border-radius: 10px; overflow: hidden;}}
                .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; }}
                .header h2 {{ margin: 0; }}
                .content {{ padding: 25px; text-align: left; color: #e0e0e0; }}
                .content p {{ margin-bottom: 15px; }}
                .highlight {{ color: #007bff; font-weight: bold; }}
                .button-link {{ display: inline-block; background-color: #007bff; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px; margin-top: 10px;}}
                .footer {{ background-color: #181818; padding: 20px; text-align: center; font-size: 0.9em; color: #888; border-top: 1px solid #222;}}
                .footer img {{ max-width: 200px; height: auto; margin-bottom: 10px; }}
                a {{ color: #007bff; }}
                a:hover {{ text-decoration: underline; }}
            </style>
        </head>
    <body>
        <div class="email-container">
            <div class="header">
                <h2>¡Bienvenido/a a Ajuma Training Center!</h2>
            </div>
            <div class="content">
                <p>Hola <strong>{nombre}</strong>,</p>
                <p>¡Gracias por registrarte en <span class="highlight">Ajuma Training Center</span>!</p>
                <p>Para activar tu membresía y comenzar a disfrutar de nuestros servicios, realiza tu primer pago haciendo clic en el siguiente botón:</p>
                <p><a href="{link_pago}" class="button-link">Realizar Pago Ahora</a></p>
                <p>Si tienes alguna consulta o necesitas ayuda, no dudes en <a href="mailto:{REMITENTE_EMAIL}?subject=Consulta%20de%20bienvenida">contactarnos</a>.</p>
                <p>¡Te esperamos!</p>
            </div>
            <div class="footer">
                <img src="cid:logo-ajuma.png" alt="Logo Ajuma Training Center">
                <p><strong>El equipo de Ajuma Training Center</strong></p>
                <p>Si no puedes ver la imagen, visita nuestro <a href="[ENLACE_A_TU_SITIO_WEB]">sitio web</a>.</p>
            </div>
        </div>
    </body>
    </html>
    """
    msg.add_alternative(cuerpo_html, subtype='html')  # Se añade la versión HTML al correo

    # === Se adjunta el logo de forma embebida para mostrarlo en el pie del email ===
    import os
    logo_path = os.path.join(os.path.dirname(__file__), "logo-ajuma.png")  # Ruta del archivo del logo
    if os.path.exists(logo_path):
        with open(logo_path, 'rb') as img:
            msg.get_payload()[1].add_related(
                img.read(),
                maintype='image',
                subtype='png',
                cid="<logo-ajuma.png>"  # ID que se usa en el HTML con "cid:"
            )

    # === ENVÍO DEL CORREO POR SMTP SEGURo (SSL) ===
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.login(REMITENTE_EMAIL, REMITENTE_PASSWORD)  # Se inicia sesión
        smtp.send_message(msg)  # Se envía el correo

    return True  # Si todo salió bien, se retorna True
