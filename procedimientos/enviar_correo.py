import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from utils.get_resorce_path import resource_path
from decouple import AutoConfig

config = AutoConfig(resource_path('.env'))


def enviar_correo(asunto: str, mensaje: str):
    try:

        # Crear el contenido del correo
        msg = MIMEMultipart()
        msg['Subject'] = asunto
        msg['From'] = config('SMTP_USERNAME')
        msg['To'] = config('SMTP_MAIL_TO')

        # Crear un objeto MIMEText para el cuerpo del mensaje
        mensaje = mensaje.encode('utf-8').decode('utf-8')
        msg.attach(MIMEText(mensaje, 'plain', 'utf-8'))

        # Crear la conexión al servidor de correo
        server = smtplib.SMTP(host=config('SMTP_SERVER'), port=config('SMTP_PORT', cast=int))
        server.starttls()  # Conexión segura
        server.login(user=config('SMTP_USERNAME'), password=config('SMTP_PASSWORD'))

        # Enviar el correo
        server.sendmail(from_addr=config('SMTP_USERNAME'),
                        to_addrs=config('SMTP_MAIL_TO'),
                        msg=msg.as_string())

        # Cerrar la conexión con el servidor
        server.quit()

    except Exception as e:
        raise e


def test_correo(server_smtp: str, port: int, user_name: str, password_mail: str, to_mail: str):
    try:

        msg_text = ("Este es un correo de prueba "
                    "desde el Software AutoparkMx "
                    "favor de no responder")

        # Crear el contenido del correo
        msg = MIMEMultipart()
        msg['Subject'] = "Prueba de Correo"
        msg['From'] = user_name
        msg['To'] = to_mail

        # Crear un objeto MIMEText para el cuerpo del mensaje
        mensaje = msg_text.encode('utf-8').decode('utf-8')
        msg.attach(MIMEText(mensaje, 'plain', 'utf-8'))

        # Crear la conexión al servidor de correo
        server = smtplib.SMTP(host=server_smtp, port=port)
        server.starttls()  # Conexión segura
        server.login(user=user_name, password=password_mail)

        # Enviar el correo
        server.sendmail(from_addr=user_name,
                        to_addrs=to_mail,
                        msg=msg.as_string())

        # Cerrar la conexión con el servidor
        server.quit()

    except Exception as e:
        raise e


if __name__ == "__main__":
    pass
