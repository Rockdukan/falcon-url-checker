import falcon

from app.resources.domain_check import DomainCheckResource
from app.resources.health import HealthResource
from app.resources.openapi_docs import register_openapi_routes


def register_routes(app: falcon.App) -> None:
    """
    Регистрирует маршруты API.

    Args:
        app: Экземпляр Falcon-приложения.
    """
    app.add_route("/api/v1/domain-check", DomainCheckResource())
    app.add_route("/api/v1/health", HealthResource())
    register_openapi_routes(app)
