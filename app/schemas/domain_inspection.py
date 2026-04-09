from pydantic import BaseModel, Field


class DnsRecords(BaseModel):
    """Снимок DNS-записей по основным типам."""
    a: list[str] = Field(default_factory=list)
    aaaa: list[str] = Field(default_factory=list)
    cname: list[str] = Field(default_factory=list)
    mx: list[str] = Field(default_factory=list)



class SslSummary(BaseModel):
    """Итог проверки TLS-сертификата на порту 443."""
    valid_until_iso: str | None = None
    not_after_raw: str | None = None
    subject: str | None = None
    issuer: str | None = None
    error: str | None = None



class HttpSummary(BaseModel):
    """Ответ главной страницы и цепочка редиректов."""
    attempted_url: str
    status_code: int | None = None
    redirect_chain: list[str] = Field(default_factory=list)
    error: str | None = None



class PortProbe(BaseModel):
    """Результат проверки одного TCP-порта."""
    port: int
    open: bool
    error: str | None = None



class WebAssetStatus(BaseModel):
    """Наличие файла по URL и код ответа."""
    checked_url: str
    exists: bool
    status_code: int | None = None
    error: str | None = None



class WebAssetsSummary(BaseModel):
    """Служебные файлы в корне сайта."""
    robots_txt: WebAssetStatus
    sitemap_xml: WebAssetStatus



class DomainInspectionReport(BaseModel):
    """Полный отчёт инспекции домена для API."""
    domain: str
    dns: DnsRecords
    ssl: SslSummary
    http: HttpSummary
    ports: list[PortProbe]
    web_assets: WebAssetsSummary
