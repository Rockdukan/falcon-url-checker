import falcon

from app.resources.base import BaseResource
from app.services.domain_inspection import DomainInspectionService
from app.validators.domain import normalize_domain
from config.settings import get_settings


class DomainCheckResource(BaseResource):
    """Чтение сводной информации о домене: DNS, TLS, HTTP и сетевой поверхности."""
    def __init__(self, service: DomainInspectionService | None = None) -> None:
        """
        Args:
            service: Сервис инспекции; по умолчанию создаётся от настроек окружения.
        """
        self.service = service or DomainInspectionService(get_settings())

    def on_get(self, req: falcon.Request, resp: falcon.Response) -> None:
        """
        Возвращает JSON-отчёт по параметру `domain`.

        Args:
            req: Запрос Falcon.
            resp: Ответ Falcon.
        """
        domain_param = req.get_param("domain", default="")

        try:
            domain = normalize_domain(domain_param)
        except ValueError as exc:
            raise falcon.HTTPBadRequest(description=str(exc)) from exc

        report = self.service.build_report(domain)
        resp.media = report.model_dump()
