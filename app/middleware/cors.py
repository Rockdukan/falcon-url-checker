import falcon


class CorsMiddleware:
    """Добавляет базовые CORS-заголовки к ответу."""

    def process_response(
        self,
        req: falcon.Request,
        resp: falcon.Response,
        resource: object,
        req_succeeded: bool,
    ) -> None:
        """
        Устанавливает заголовки CORS перед отправкой ответа.

        Args:
            req: Запрос.
            resp: Ответ.
            resource: Обработчик ресурса (если найден).
            req_succeeded: Флаг успешной обработки.
        """
        resp.set_header("Access-Control-Allow-Origin", "*")
        resp.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        resp.set_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
