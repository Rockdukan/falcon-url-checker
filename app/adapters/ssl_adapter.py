import socket
import ssl
from datetime import UTC, datetime


class SslAdapter:
    """TLS-хендшейк и чтение метаданных сертификата с удалённого хоста."""
    def __init__(self, connect_timeout: float = 5.0) -> None:
        """
        Args:
            connect_timeout: Таймаут установки TCP-соединения в секундах.
        """
        self.connect_timeout = connect_timeout

    def peer_certificate_summary(self, host: str, port: int = 443) -> dict[str, str | None]:
        """
        Подключается к хосту и возвращает срок действия и субъект сертификата.

        Args:
            host: Имя хоста (SNI).
            port: Порт TLS (по умолчанию 443).

        Returns:
            Словарь с ключами `valid_until_iso`, `not_after_raw`, `subject`,
            `issuer`, `error`. При ошибке подключения заполняется только `error`.
        """
        ctx = ssl.create_default_context()

        try:
            with socket.create_connection((host, port), timeout=self.connect_timeout) as sock:
                with ctx.wrap_socket(sock, server_hostname=host) as tls_sock:
                    cert = tls_sock.getpeercert()
        except (OSError, TimeoutError, ssl.SSLError) as exc:
            return {
                "valid_until_iso": None,
                "not_after_raw": None,
                "subject": None,
                "issuer": None,
                "error": str(exc),
            }

        if not cert:
            return {
                "valid_until_iso": None,
                "not_after_raw": None,
                "subject": None,
                "issuer": None,
                "error": "Сертификат недоступен (возможно, анонимный шифр)",
            }

        not_after = cert.get("notAfter")
        valid_until_iso: str | None = None

        if not_after:
            try:
                dt = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
                valid_until_iso = dt.replace(tzinfo=UTC).isoformat()
            except ValueError:
                valid_until_iso = None

        subject = self.format_x509_tuple(cert.get("subject"))
        issuer = self.format_x509_tuple(cert.get("issuer"))

        return {
            "valid_until_iso": valid_until_iso,
            "not_after_raw": not_after,
            "subject": subject,
            "issuer": issuer,
            "error": None,
        }

    def format_x509_tuple(self, name: object) -> str | None:
        """
        Сводит кортеж subject/issuer из `getpeercert()` в читаемую строку.

        Args:
            name: Структура из `ssl`-модуля или `None`.

        Returns:
            Строка вида `CN=example.com, O=...` либо `None`.
        """
        if not name:
            return None

        parts: list[str] = []

        if isinstance(name, tuple):
            for seq in name:
                for key, value in seq:
                    parts.append(f"{key}={value}")

            return ", ".join(parts)

        return str(name)
