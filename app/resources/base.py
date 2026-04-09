import falcon


class BaseResource:
    """Общий предок ресурсов с заготовкой под общую логику."""

    def on_options(self, req: falcon.Request, resp: falcon.Response) -> None:
        """
        Отвечает на preflight OPTIONS для браузерных fetch/XHR.

        Args:
            req: Запрос.
            resp: Ответ.
        """
        resp.status = falcon.HTTP_204
