import re
from urllib.parse import urlparse

_DOMAIN_LABEL = r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)"
_HOST_PATTERN = re.compile(
    rf"^(?:{_DOMAIN_LABEL}\.)*{_DOMAIN_LABEL}\.?$",
    re.IGNORECASE,
)


def normalize_domain(raw: str) -> str:
    """
    Нормализует ввод и возвращает доменное имя в нижнем регистре.

    Поддерживает схему `http(s)://`, отбрасывает завершающую точку.

    Args:
        raw: Строка от пользователя (домен, URL или пустая строка).

    Returns:
        Нормализованный домен (без завершающей точки).

    Raises:
        ValueError: Если строка пустая, не похожа на домен или выглядит как email.
    """
    value = (raw or "").strip().lower()

    if not value:
        raise ValueError("Укажите домен или URL")

    if value.startswith("http://") or value.startswith("https://"):
        parsed = urlparse(value)
        value = (parsed.hostname or "").lower()

        if not value:
            raise ValueError("Не удалось извлечь домен из URL")

    if "@" in value:
        raise ValueError("Ожидается домен или URL, а не email")

    if value.endswith("."):
        value = value[:-1]

    if len(value) > 253:
        raise ValueError("Слишком длинное доменное имя")

    if not _HOST_PATTERN.match(value):
        raise ValueError("Некорректное доменное имя")

    return value
