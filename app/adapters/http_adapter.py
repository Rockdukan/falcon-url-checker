import httpx


class HttpAdapter:
    """HTTP-клиент для статуса ответа и цепочки редиректов."""
    def __init__(self, timeout: float = 10.0) -> None:
        """
        Args:
            timeout: Таймаут запроса в секундах (для connect и read одинаковый).
        """
        self.timeout = timeout

    def fetch_home(self, start_url: str) -> dict[str, object]:
        """
        Выполняет GET по указанному URL с автоматическим следованием редиректам.

        Args:
            start_url: Полный URL (обычно `https://example.com/`).

        Returns:
            Поля `url`, `status_code`, `redirect_chain`, `error`.
        """
        timeout = httpx.Timeout(self.timeout, connect=min(5.0, self.timeout))

        try:
            with httpx.Client(follow_redirects=True, timeout=timeout) as client:
                response = client.get(start_url)
        except httpx.RequestError as exc:
            return {
                "url": start_url,
                "status_code": None,
                "redirect_chain": [start_url],
                "error": str(exc),
            }

        chain = [str(hist.url) for hist in response.history] + [str(response.url)]

        return {
            "url": start_url,
            "status_code": response.status_code,
            "redirect_chain": chain,
            "error": None,
        }
