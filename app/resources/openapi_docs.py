from pathlib import Path

import falcon
import yaml

APP_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = APP_ROOT.parent
OPENAPI_YAML_PATH = APP_ROOT / "openapi" / "openapi.yaml"
SWAGGER_INDEX_PATH = REPO_ROOT / "templates" / "swagger_index.html"
REDOC_HTML_PATH = REPO_ROOT / "templates" / "redoc.html"


class OpenApiYamlResource:
    """Отдаёт каноническую спецификацию OpenAPI в YAML."""

    def on_get(self, req: falcon.Request, resp: falcon.Response) -> None:
        """
        Читает `app/openapi/openapi.yaml` и возвращает как `text/yaml`.

        Args:
            req: Запрос Falcon.
            resp: Ответ Falcon.

        Raises:
            falcon.HTTPNotFound: Если файл спецификации отсутствует на диске.
        """

        if not OPENAPI_YAML_PATH.is_file():
            raise falcon.HTTPNotFound(description="Файл app/openapi/openapi.yaml не найден")

        resp.content_type = "text/yaml; charset=utf-8"
        resp.text = OPENAPI_YAML_PATH.read_text(encoding="utf-8")


class OpenApiJsonResource:
    """Публикует ту же спецификацию в JSON (удобно для сторонних клиентов)."""

    def on_get(self, req: falcon.Request, resp: falcon.Response) -> None:
        """
        Парсит YAML и отдаёт объект, который Falcon сериализует в JSON.

        Args:
            req: Запрос Falcon.
            resp: Ответ Falcon.

        Raises:
            falcon.HTTPNotFound: Если файл спецификации отсутствует.
            falcon.HTTPInternalServerError: Если YAML повреждён.
        """

        if not OPENAPI_YAML_PATH.is_file():
            raise falcon.HTTPNotFound(description="Файл app/openapi/openapi.yaml не найден")

        raw = OPENAPI_YAML_PATH.read_text(encoding="utf-8")

        try:
            data = yaml.safe_load(raw)
        except yaml.YAMLError as exc:
            raise falcon.HTTPInternalServerError(description="Некорректный OpenAPI YAML") from exc

        resp.media = data


class SwaggerDocsResource:
    """HTML-оболочка Swagger UI; статические бандлы лежат под `/swagger-ui/`."""

    def on_get(self, req: falcon.Request, resp: falcon.Response) -> None:
        """
        Отдаёт страницу из `templates/swagger_index.html`.

        Args:
            req: Запрос Falcon.
            resp: Ответ Falcon.

        Raises:
            falcon.HTTPNotFound: Если шаблон отсутствует.
        """

        if not SWAGGER_INDEX_PATH.is_file():
            raise falcon.HTTPNotFound(description="Шаблон templates/swagger_index.html не найден")

        resp.content_type = "text/html; charset=utf-8"
        resp.text = SWAGGER_INDEX_PATH.read_text(encoding="utf-8")


class RedocDocsResource:
    """Статическая страница ReDoc с `spec-url` на `/openapi.yaml`."""

    def on_get(self, req: falcon.Request, resp: falcon.Response) -> None:
        """
        Отдаёт `templates/redoc.html`.

        Args:
            req: Запрос Falcon.
            resp: Ответ Falcon.

        Raises:
            falcon.HTTPNotFound: Если шаблон отсутствует.
        """

        if not REDOC_HTML_PATH.is_file():
            raise falcon.HTTPNotFound(description="Шаблон templates/redoc.html не найден")

        resp.content_type = "text/html; charset=utf-8"
        resp.text = REDOC_HTML_PATH.read_text(encoding="utf-8")


def register_openapi_routes(app: falcon.App) -> None:
    """
    Подключает раздачу спецификации, Swagger UI и ReDoc.

    Args:
        app: Экземпляр Falcon-приложения.
    """

    swagger_dir = REPO_ROOT / "static" / "swagger"

    if swagger_dir.is_dir():
        app.add_static_route("/swagger-ui", str(swagger_dir))

    app.add_route("/openapi.yaml", OpenApiYamlResource())
    app.add_route("/openapi.json", OpenApiJsonResource())
    app.add_route("/docs", SwaggerDocsResource())
    app.add_route("/redoc", RedocDocsResource())
