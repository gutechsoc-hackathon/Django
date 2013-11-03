from django.core.mail import EmailMessage

def sendmail(subject, message, to):
    email = EmailMessage(subject, message, to=[to])
    email.send()
