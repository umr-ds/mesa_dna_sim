from flask_mail import Mail, Message
from flask import current_app

mail = Mail()


def send_mail(sender, recipients, text, subject="Confirmation Link for MOSLA-DNASimulator"):
    with current_app.app_context():
        msg = Message(subject, body=text,
                      sender=current_app.config.get("MAIL_USERNAME"), recipients=recipients)
        mail.send(msg)
