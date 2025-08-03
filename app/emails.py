#here we will be defining methods that send emails. 
from flask_mail import Message
from app import mail, app
from flask import render_template
from threading import Thread

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, bodytext, bodyhtml):
    msg = Message(subject=subject, sender=sender, recipients= recipients)
    msg.body = bodytext
    msg.html = bodyhtml
    #create a thread that runs in the background to send the email
    Thread(target=send_async_email, args=(app, msg)).start()
    

def send_password_reset_request_email(user):
    #make token.
    token = user.generate_token()
    send_email('[Microblog] reset password ', sender = app.config['ADMINS'][0], recipients=[user.email],
                bodytext= render_template('reset_password_emails/reset_password.txt', user=user, token= token),
                bodyhtml= render_template('reset_password_emails/reset_password.html', user=user, token= token)
                )
    