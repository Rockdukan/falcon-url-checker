import logging

import falcon

logger = logging.getLogger("app")


class RequestLoggerMiddleware:
    """Пишет метод и путь каждого запроса на уровне INFO."""

    def process_request(self, req: falcon.Request, resp: falcon.Response) -> None:
        """
        Логирует входящий запрос.

        Args:
            req: Запрос.
            resp: Ответ.
        """
        logger.info("%s %s", req.method, req.path)
