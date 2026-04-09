import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Прикладные настройки, читаемые из окружения."""
    APP_NAME: str = "falcon-base"
    DEBUG: bool = False
    DNS_RESOLVER_LIFETIME: float = 8.0
    SSL_CONNECT_TIMEOUT: float = 5.0
    HTTP_CLIENT_TIMEOUT: float = 10.0
    PORT_PROBE_TIMEOUT: float = 0.45
    SCAN_PORTS: list[int] = Field(
        default_factory=lambda: [
            21,
            22,
            25,
            53,
            80,
            110,
            143,
            443,
            465,
            587,
            993,
            995,
            8080,
            8443,
        ],
    )

    def effective_scan_ports(self) -> list[int]:
        """
        Возвращает список портов для сканирования (на будущее — с учётом окружения).

        Returns:
            Упорядоченный набор портов без дубликатов на уровне адаптера.
        """
        return self.SCAN_PORTS


@lru_cache
def get_settings() -> Settings:
    """
    Возвращает singleton настроек после загрузки `.env`.

    Returns:
        Экземпляр `Settings`.
    """
    load_dotenv()

    scan_csv = os.environ.get("SCAN_PORTS", "").strip()
    scan_ports: list[int] | None = None

    if scan_csv:
        scan_ports = [int(chunk) for chunk in scan_csv.split(",") if chunk.strip()]

    data = {
        "APP_NAME": os.environ.get("APP_NAME", "falcon-base"),
        "DEBUG": os.environ.get("DEBUG", "false").lower() in ("1", "true", "yes", "on"),
        "DNS_RESOLVER_LIFETIME": float(os.environ.get("DNS_RESOLVER_LIFETIME", "8") or 8),
        "SSL_CONNECT_TIMEOUT": float(os.environ.get("SSL_CONNECT_TIMEOUT", "5") or 5),
        "HTTP_CLIENT_TIMEOUT": float(os.environ.get("HTTP_CLIENT_TIMEOUT", "10") or 10),
        "PORT_PROBE_TIMEOUT": float(os.environ.get("PORT_PROBE_TIMEOUT", "0.45") or 0.45),
    }

    if scan_ports is not None:
        data["SCAN_PORTS"] = scan_ports

    return Settings(**data)
