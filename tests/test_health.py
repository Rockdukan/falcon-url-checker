from webtest import TestApp

from app import create_app


def test_health_ok() -> None:
    """Эндпоинт health отвечает JSON со статусом ok."""
    app = create_app()
    client = TestApp(app)
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json == {"status": "ok"}
