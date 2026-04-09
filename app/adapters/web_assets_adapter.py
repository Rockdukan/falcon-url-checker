import httpx


class WebAssetsAdapter:
    """Проверка наличия типовых файлов в корне сайта."""
    def __init__(self, timeout: float = 8.0) -> None:
        """
        Args:
            timeout: Таймаут HEAD-запроса в секундах.
        """
        self.timeout = timeout

    def check_pair(self, base_https: str, base_http: str | None) -> dict[str, dict[str, object]]:
        """
        Проверяет `robots.txt` и `sitemap.xml` на HTTPS, при сбое — на HTTP.

        Args:
            base_https: Например `https://example.com`.
            base_http: Например `http://example.com` или `None`, если не проверять.

        Returns:
            Вложенный словарь с ключами `robots_txt` и `sitemap_xml`.
        """
        timeout = httpx.Timeout(self.timeout, connect=min(4.0, self.timeout))

        return {
            "robots_txt": self.probe_asset(
                [f"{base_https}/robots.txt", f"{base_http}/robots.txt"] if base_http else [f"{base_https}/robots.txt"],
                timeout,
            ),
            "sitemap_xml": self.probe_asset(
                (
                    [f"{base_https}/sitemap.xml", f"{base_http}/sitemap.xml"]
                    if base_http
                    else [f"{base_https}/sitemap.xml"]
                ),
                timeout,
            ),
        }

    def probe_asset(self, urls: list[str], timeout: httpx.Timeout) -> dict[str, object]:
        """
        Последовательно выполняет HEAD до первого ответа без транспортной ошибки.

        Args:
            urls: Список полных URL одного ресурса (приоритет — сначала HTTPS).
            timeout: Таймаут клиента `httpx`.

        Returns:
            Поля `checked_url`, `exists`, `status_code`, `error`.
        """
        last_error: str | None = None

        with httpx.Client(follow_redirects=True, timeout=timeout) as client:
            for url in urls:
                try:
                    response = client.head(url)
                except httpx.RequestError as exc:
                    last_error = str(exc)

                    continue

                exists = response.status_code == 200

                return {
                    "checked_url": url,
                    "exists": exists,
                    "status_code": response.status_code,
                    "error": None,
                }

        return {
            "checked_url": urls[-1] if urls else "",
            "exists": False,
            "status_code": None,
            "error": last_error or "Не удалось выполнить запрос",
        }
