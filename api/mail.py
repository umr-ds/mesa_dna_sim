from flask_mail import Mail, Message
from flask import current_app

mail = Mail()


def send_mail(sender, recipients, text):
    """
    Sends an email to passed recipients with the passed text.
    :param sender:
    :param recipients:
    :param text:
    :return:
    """
    with current_app.app_context():
        msg = Message("Confirmation Link for MOSLA-DNASimulator", body=text,
                      sender=current_app.config.get("MAIL_USERNAME"), recipients=recipients)
        mail.send(msg)
