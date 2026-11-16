"""Generic SMTP backend (Mailtrap sandbox and production SMTP)."""

from __future__ import annotations

import logging
import smtplib
import ssl

from vendor.messaging.backends.stdlib_mime import stdlib_email_message_class
from vendor.messaging.config import MessagingSettings
from vendor.messaging.types import EmailMessage, SendResult

logger = logging.getLogger(__name__)


class SmtpBackend:
    provider_name = "smtp"

    def __init__(self, settings: MessagingSettings) -> None:
        self._settings = settings

    def send(self, message: EmailMessage) -> SendResult:
        from_header = message.from_address or self._settings.email_from
        root = stdlib_email_message_class()()
        root["Subject"] = message.subject
        root["From"] = from_header
        root["To"] = (
            f"{message.to_name} <{message.to_address}>"
            if message.to_name
            else message.to_address
        )
        if message.reply_to:
            root["Reply-To"] = message.reply_to
        for key, value in message.headers.items():
            root[key] = value
        root.set_content(message.body_text)

        host = self._settings.smtp_host
        port = self._settings.smtp_port
        user = self._settings.smtp_user
        password = self._settings.smtp_password
        timeout = self._settings.smtp_timeout

        try:
            if self._settings.smtp_ssl:
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(host, port, timeout=timeout, context=context) as smtp:
                    if user:
                        smtp.login(user, password)
                    smtp.send_message(root)
            else:
                with smtplib.SMTP(host, port, timeout=timeout) as smtp:
                    if self._settings.smtp_starttls:
                        context = ssl.create_default_context()
                        smtp.starttls(context=context)
                    if user:
                        smtp.login(user, password)
                    smtp.send_message(root)
        except smtplib.SMTPException as exc:
            logger.warning("SMTP send failed to %s: %s", message.to_address, exc)
            return SendResult(ok=False, provider=self.provider_name, detail=str(exc))
        except OSError as exc:
            logger.warning("SMTP connection failed to %s:%s: %s", host, port, exc)
            return SendResult(ok=False, provider=self.provider_name, detail=str(exc))

        return SendResult(ok=True, provider=self.provider_name, detail="sent")