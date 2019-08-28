from flask_mail import Mail, Message
from flask import current_app

mail = Mail()


def send_mail(sender, recipients, text, subject="Confirmation Link for MOSLA-DNASimulator"):
    """
    Sends an email to passed recipients with the passed text.
    :param sender:
    :param recipients:
    :param text:
    :return:
    """
    if sender is None:
        sender = current_app.config.get("MAIL_USERNAME")
    with current_app.app_context():
        msg = Message(subject, body=text, sender=sender, recipients=recipients)
        mail.send(msg)
