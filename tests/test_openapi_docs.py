from webtest import TestApp

from app import create_app


def test_openapi_yaml_served() -> None:
    """Эндпоинт /openapi.yaml отдаёт YAML со строкой openapi: 3.0.3."""
    app = create_app()
    client = TestApp(app)
    response = client.get("/openapi.yaml")

    assert response.status_code == 200
    assert "openapi: 3.0.3" in response.text
    assert "text/yaml" in response.headers.get("Content-Type", "")


def test_openapi_json_served() -> None:
    """Эндпоинт /openapi.json отдаёт JSON с тем же корнем."""
    app = create_app()
    client = TestApp(app)
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert response.json["openapi"] == "3.0.3"


def test_docs_and_redoc_html() -> None:
    """Страницы документации отдаются как HTML."""
    app = create_app()
    client = TestApp(app)

    docs = client.get("/docs")
    redoc = client.get("/redoc")

    assert docs.status_code == 200
    assert "swagger-ui" in docs.text
    assert docs.headers.get("Content-Type", "").startswith("text/html")

    assert redoc.status_code == 200
    assert "openapi.yaml" in redoc.text
    assert redoc.headers.get("Content-Type", "").startswith("text/html")


def test_swagger_ui_static_bundle() -> None:
    """Статический бандл Swagger UI доступен по префиксу /swagger-ui/."""
    app = create_app()
    client = TestApp(app)
    response = client.get("/swagger-ui/swagger-ui.css")

    assert response.status_code == 200
    assert len(response.body) > 1000
