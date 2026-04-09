import logging

import falcon

logger = logging.getLogger("app")


def register_error_handlers(app: falcon.App) -> None:
    """
    Подключает обработчик необработанных исключений.

    Args:
        app: Экземпляр Falcon-приложения.
    """

    def handle_uncaught(req: falcon.Request, resp: falcon.Response, ex: Exception, params: dict) -> None:
        """
        Логирует исключение и отдаёт 500 без утечки деталей.

        Args:
            req: Запрос Falcon.
            resp: Ответ Falcon.
            ex: Исключение.
            params: Параметры маршрута.
        """
        logger.exception("Необработанное исключение")
        resp.status = falcon.HTTP_500
        resp.media = {"detail": "Внутренняя ошибка сервера"}

    app.add_error_handler(Exception, handle_uncaught)
