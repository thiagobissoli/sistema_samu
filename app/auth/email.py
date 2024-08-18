from flask import url_for
from flask_mail import Message
from app import mail

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    msg = Message('Reset Your Password',
                  sender='noreply@example.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('auth.reset_password', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)
