from flask_mail import Mail, Message
from flask import current_app

mail = Mail()


def send_mail(sender, recipients, text, subject="Confirmation Link for MOSLA-DNASimulator", attachment_txt=None,
              attachment_name=None):
    """
    Sends an email to passed recipients with the passed text.
    :param attachment_name:
    :param subject:
    :param attachment_txt:
    :param sender:
    :param recipients:
    :param text:
    :return:
    """
    if not current_app.config['MAIL_ENABLED']:
        return
    if sender is None:
        sender = current_app.config.get("MAIL_SENDER_ALIAS")
    with current_app.app_context():
        msg = Message(subject, body=text, sender=sender, recipients=recipients)
        if attachment_txt is not None:
            if attachment_name is None:
                attachment_name = "mosla.fastq"
            msg.attach(filename=attachment_name, content_type="text/plain", data=attachment_txt)
        try:
            mail.send(msg)
        except Exception as ex:
            print(ex)
