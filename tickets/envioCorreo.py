from email.message import EmailMessage
import random
from django.core.mail import send_mail, get_connection, EmailMessage
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
import json
class Correo():
    def envioCorreos(**kwargs):
        email_credentials = settings.EMAIL_HOST_USER[kwargs['correoSend']]
        user=email_credentials['user'] 
        passW=email_credentials['pass']
        with get_connection(  
            host=settings.EMAIL_HOST, 
            port=settings.EMAIL_PORT,  
            username=user, 
            password=passW, 
            use_tls=settings.EMAIL_USE_TLS  
        ) as connection: 
            emailTo = kwargs['emailTo']
            emailCC = kwargs['emailCC']
            asunto = kwargs['asunto']
            mensaje = kwargs['mensaje']
            
            recipient_list = emailTo.split(',') if emailTo else []
            recipient_list = [email.strip() for email in recipient_list]
            cc_list = emailCC.split(',') if emailCC else []
            cc_list = [email.strip() for email in cc_list]
            try:
                email = EmailMessage(asunto, mensaje, user, recipient_list, cc=cc_list,connection=connection)
                email.send()
                return JsonResponse({'status': 'success', 'message': 'Correo enviado correctamente.'})
            except Exception as e:
                print(str(e)) 
                return JsonResponse({'status': 'error', 'message': 'Error al enviar el correo.'})
            