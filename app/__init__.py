import falcon

from app.errors import register_error_handlers
from app.middleware.cors import CorsMiddleware
from app.middleware.request_logger import RequestLoggerMiddleware
from app.routing import register_routes


def create_app() -> falcon.App:
    """
    Собирает Falcon-приложение с middleware и маршрутами.

    Returns:
        Настроенный `falcon.App`.
    """
    middleware = [CorsMiddleware(), RequestLoggerMiddleware()]
    app = falcon.App(middleware=middleware)
    register_routes(app)
    register_error_handlers(app)

    return app
