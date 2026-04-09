import falcon

from app.resources.base import BaseResource


class HealthResource(BaseResource):
    """Health-check для балансировщиков и мониторинга."""

    def on_get(self, req: falcon.Request, resp: falcon.Response) -> None:
        """
        Возвращает JSON со статусом сервиса.

        Args:
            req: Запрос.
            resp: Ответ.
        """
        resp.media = {"status": "ok"}
