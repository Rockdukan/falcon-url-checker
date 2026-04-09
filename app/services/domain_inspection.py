from app.adapters.dns_adapter import DnsAdapter
from app.adapters.http_adapter import HttpAdapter
from app.adapters.ports_adapter import PortsAdapter
from app.adapters.ssl_adapter import SslAdapter
from app.adapters.web_assets_adapter import WebAssetsAdapter
from app.schemas.domain_inspection import (
    DnsRecords,
    DomainInspectionReport,
    HttpSummary,
    PortProbe,
    SslSummary,
    WebAssetsSummary,
    WebAssetStatus,
)
from config.settings import Settings


class DomainInspectionService:
    """Оркестрация адаптеров и сбор единого отчёта по домену."""
    def __init__(self, settings: Settings) -> None:
        """
        Args:
            settings: Прикладные таймауты и список портов для сканирования.
        """
        self.settings = settings
        self.dns_adapter = DnsAdapter(lifetime=settings.DNS_RESOLVER_LIFETIME)
        self.ssl_adapter = SslAdapter(connect_timeout=settings.SSL_CONNECT_TIMEOUT)
        self.http_adapter = HttpAdapter(timeout=settings.HTTP_CLIENT_TIMEOUT)
        self.ports_adapter = PortsAdapter(connect_timeout=settings.PORT_PROBE_TIMEOUT)
        self.web_assets_adapter = WebAssetsAdapter(timeout=settings.HTTP_CLIENT_TIMEOUT)

    def build_report(self, domain: str) -> DomainInspectionReport:
        """
        Выполняет все проверки и возвращает типизированный отчёт.

        Args:
            domain: Уже нормализованное доменное имя без схемы.

        Returns:
            Модель `DomainInspectionReport` для сериализации в JSON.
        """
        dns_map = self.dns_adapter.resolve_bundle(domain)
        dns = DnsRecords(
            a=dns_map["a"],
            aaaa=dns_map["aaaa"],
            cname=dns_map["cname"],
            mx=dns_map["mx"],
        )

        ssl_raw = self.ssl_adapter.peer_certificate_summary(domain, 443)
        ssl_summary = SslSummary(
            valid_until_iso=ssl_raw["valid_until_iso"],
            not_after_raw=ssl_raw["not_after_raw"],
            subject=ssl_raw["subject"],
            issuer=ssl_raw["issuer"],
            error=ssl_raw["error"],
        )

        ports_raw = self.ports_adapter.probe_ports(domain, self.settings.effective_scan_ports())
        ports = [PortProbe(port=int(row["port"]), open=bool(row["open"]), error=row.get("error")) for row in ports_raw]

        https_home = f"https://{domain}/"
        http_home = f"http://{domain}/"
        http_primary = self.http_adapter.fetch_home(https_home)
        http_summary = self.wrap_http(https_home, http_primary)

        if http_primary["error"]:
            http_fallback = self.http_adapter.fetch_home(http_home)
            http_summary = self.wrap_http(http_home, http_fallback)

        assets_raw = self.web_assets_adapter.check_pair(f"https://{domain}", f"http://{domain}")
        web_assets = WebAssetsSummary(
            robots_txt=WebAssetStatus(
                checked_url=str(assets_raw["robots_txt"]["checked_url"]),
                exists=bool(assets_raw["robots_txt"]["exists"]),
                status_code=assets_raw["robots_txt"].get("status_code"),
                error=assets_raw["robots_txt"].get("error"),
            ),
            sitemap_xml=WebAssetStatus(
                checked_url=str(assets_raw["sitemap_xml"]["checked_url"]),
                exists=bool(assets_raw["sitemap_xml"]["exists"]),
                status_code=assets_raw["sitemap_xml"].get("status_code"),
                error=assets_raw["sitemap_xml"].get("error"),
            ),
        )

        return DomainInspectionReport(
            domain=domain,
            dns=dns,
            ssl=ssl_summary,
            http=http_summary,
            ports=ports,
            web_assets=web_assets,
        )

    def wrap_http(self, attempted_url: str, raw: dict[str, object]) -> HttpSummary:
        """
        Преобразует сырой ответ HTTP-адаптера в схему API.

        Args:
            attempted_url: URL, с которого начинали запрос.
            raw: Словарь из `HttpAdapter.fetch_home`.

        Returns:
            Модель `HttpSummary`.
        """
        chain = raw.get("redirect_chain") or [attempted_url]

        if not isinstance(chain, list):
            chain = [attempted_url]

        return HttpSummary(
            attempted_url=attempted_url,
            status_code=raw.get("status_code"),
            redirect_chain=[str(item) for item in chain],
            error=raw.get("error"),
        )
