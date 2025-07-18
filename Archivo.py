import requests 
import smtplib
import configparser
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


def configuracion():
    config = configparser.ConfigParser()
    config.read('settings.conf')
    return config


def fecha_pdf(conf):
    url = conf["url"]
    campo = conf["campo"]
    response = requests.get(url, stream=True)
    fecha = response.headers[campo]
    return fecha


def descargar_pdf(url):
    response = requests.get(url, stream=True)         
    if response.status_code == 200:
        with open('cronograma_ftp.pdf', 'wb') as f:
            for i in response.iter_content(chunk_size=8192):
                f.write(i)
        print("PDF descargado correctamente")        
    else:
        print("El PDF no se pudo descargar")




def leer_fecha_txt(archivo):
    fecha = ""
    try:
        with open(archivo, "r", encoding="latin-1") as f:
            fecha = f.readline()
    except FileNotFoundError:
        fecha = ""
    return fecha


def agregar_a_txt(archivo, fecha):
    with open(archivo, "w", encoding="utf-8") as f:
        f.write(fecha)


def parsear(s):
    fecha_estructurada = datetime.strptime(s, "%a, %d %b %Y %H:%M:%S %Z")
    return fecha_estructurada




# textfile = 'FechaPDF.txt'



def enviar_email(conf, fecha):
    url = conf["url"]
    sender_email = conf["sender_email"]  
    receiver_emails = conf["receiver_emails"].split(",")
    smtp_server = conf["smtp_server"]  
    smtp_port = int(conf["smtp_port"])
    fecha_estructurada = parsear(fecha)
    
    
    s = f"""El archivo del cronograma FTP fue modificado el {fecha_estructurada}
    {url}
        
    O.S.P.I.A Sistemas    
        """
    
    message = MIMEMultipart()
    message["Subject"] = f"Cronograma FTP actualizado ({fecha_estructurada})"
    message["From"] = sender_email
    message["To"] = ", ".join(receiver_emails)
    message.attach(MIMEText(s, "plain"))

        
    with open('cronograma_ftp.pdf', 'rb') as attachment:
        adjunto = MIMEBase('application', 'octet-stream')
        adjunto.set_payload(attachment.read())
        encoders.encode_base64(adjunto) 
        adjunto.add_header('Content-Disposition', f'attachment; filename= cronograma_ftp.pdf')
        message.attach(adjunto)
        

    
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.sendmail(
                f"OSPIA Sistemas <{sender_email}>", receiver_emails, message.as_string())
            print("Email sent successfully!")
    except smtplib.SMTPException as e:
        print(f"Error: Unable to send email. {e}")

    
            

if __name__ == "__main__":
    conf = configuracion()['comprobantes_ftp']
    archivo = conf['archivo']
    url = conf['url']
    fecha_guardada = leer_fecha_txt(archivo)
    fecha_nueva = fecha_pdf(conf)
    if fecha_guardada != fecha_nueva:
        print("la fecha cambió", fecha_nueva)
        agregar_a_txt(archivo, fecha_nueva)
        descargar_pdf(url)
        enviar_email(conf, fecha_nueva)
    else:
        print("la fecha es la misma: ", fecha_nueva)
        
        
        