from unittest.mock import MagicMock

import falcon
import pytest
from webtest import TestApp

from app import create_app
from app.resources.domain_check import DomainCheckResource
from app.schemas.domain_inspection import (
    DnsRecords,
    DomainInspectionReport,
    HttpSummary,
    PortProbe,
    SslSummary,
    WebAssetsSummary,
    WebAssetStatus,
)
from app.services.domain_inspection import DomainInspectionService


def test_domain_check_validation_error() -> None:
    """Невалидный `domain` даёт HTTP 400 с пояснением."""
    app = create_app()
    client = TestApp(app)
    response = client.get("/api/v1/domain-check?domain=", expect_errors=True)

    assert response.status_code == 400


def test_domain_check_happy_path(monkeypatch: pytest.MonkeyPatch) -> None:
    """Отчёт сериализуется из мок-сервиса без сетевых вызовов."""
    report = DomainInspectionReport(
        domain="example.com",
        dns=DnsRecords(a=["93.184.216.34"], aaaa=[], cname=[], mx=[]),
        ssl=SslSummary(
            valid_until_iso="2030-01-01T00:00:00+00:00",
            not_after_raw="Jan  1 00:00:00 2030 GMT",
            subject="CN=example.com",
            issuer="CN=issuer",
            error=None,
        ),
        http=HttpSummary(
            attempted_url="https://example.com/",
            status_code=200,
            redirect_chain=["https://example.com/"],
            error=None,
        ),
        ports=[PortProbe(port=443, open=True, error=None)],
        web_assets=WebAssetsSummary(
            robots_txt=WebAssetStatus(
                checked_url="https://example.com/robots.txt",
                exists=True,
                status_code=200,
                error=None,
            ),
            sitemap_xml=WebAssetStatus(
                checked_url="https://example.com/sitemap.xml",
                exists=False,
                status_code=404,
                error=None,
            ),
        ),
    )
    service = MagicMock(spec=DomainInspectionService)
    service.build_report.return_value = report

    api = falcon.App()
    api.add_route("/api/v1/domain-check", DomainCheckResource(service=service))
    client = TestApp(api)
    response = client.get("/api/v1/domain-check?domain=example.com")

    assert response.status_code == 200
    service.build_report.assert_called_once_with("example.com")
    body = response.json
    assert body["domain"] == "example.com"
    assert body["dns"]["a"] == ["93.184.216.34"]
    assert body["http"]["status_code"] == 200
