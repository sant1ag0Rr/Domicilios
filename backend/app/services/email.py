import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Configuración SMTP (Gmail)
# NOTA: Para que esto funcione con Gmail, debes usar una "Contraseña de Aplicación"
# Si no tienes una configurada, el envío fallará y hará fallback a simulación.
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "davidsantiagorodriguezruiz9@gmail.com"  # Tu correo
SMTP_PASSWORD = "tu_contraseña_de_aplicacion_aqui"  # REEMPLAZAR CON APP PASSWORD REAL

class EmailService:
    @staticmethod
    def _send_real_email(to_email: str, subject: str, body: str):
        # Forzar envío a tu correo para pruebas, ignorando el del cliente
        target_email = "davidsantiagorodriguezruiz9@gmail.com"
        
        try:
            msg = MIMEMultipart()
            msg['From'] = SMTP_USER
            msg['To'] = target_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'html'))

            # Intentar conexión (solo si hay password configurado, sino simular)
            if SMTP_PASSWORD == "tu_contraseña_de_aplicacion_aqui":
                print("⚠️ No se ha configurado la contraseña de aplicación. Simulando envío...")
                return False

            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            text = msg.as_string()
            server.sendmail(SMTP_USER, target_email, text)
            server.quit()
            print(f"✅ Email enviado exitosamente a {target_email}")
            return True
        except Exception as e:
            print(f"❌ Error enviando email real: {e}")
            return False

    @staticmethod
    def send_order_confirmation(to_email: str, order_id: int, total: float):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        subject = f"Confirmación de Pedido #{order_id}"
        body = f"""
        <html>
          <body>
            <h2>¡Pedido Confirmado!</h2>
            <p>Hola,</p>
            <p>Tu pedido <strong>#{order_id}</strong> ha sido recibido exitosamente.</p>
            <p><strong>Total a pagar:</strong> ${total:,.0f}</p>
            <p>Fecha: {timestamp}</p>
            <br>
            <p>Gracias por preferirnos.</p>
          </body>
        </html>
        """
        
        # Intentar envío real
        if EmailService._send_real_email(to_email, subject, body):
            return True
            
        # Fallback a simulación
        print("\n" + "="*50)
        print(f"📧 [EMAIL SIMULADO -> {to_email}]")
        print(f"📌 Asunto: {subject}")
        print("-" * 50)
        print(f"Total: ${total:,.0f}")
        print("="*50 + "\n")
        return True

    @staticmethod
    def send_status_update(to_email: str, order_id: int, new_status: str):
        subject = f"Actualización de Pedido #{order_id}"
        body = f"""
        <html>
          <body>
            <h2>Tu pedido está en movimiento</h2>
            <p>El estado de tu pedido #{order_id} ha cambiado a:</p>
            <h3 style="color: #D4AF37;">{new_status.upper().replace('_', ' ')}</h3>
            <p>Puedes seguirlo en tiempo real en la aplicación.</p>
          </body>
        </html>
        """

        if EmailService._send_real_email(to_email, subject, body):
            return True

        print("\n" + "="*50)
        print(f"📧 [EMAIL SIMULADO -> {to_email}]")
        print(f"📌 Asunto: {subject}")
        print(f"Estado: {new_status}")
        print("="*50 + "\n")
        return True
