# Falcon URL Checker

Сервис на **Falcon**: проверка домена/URL — DNS (A, AAAA, CNAME, MX), срок TLS-сертификата, HTTP-статус и цепочка редиректов, доступность TCP-портов, наличие `robots.txt` и `sitemap.xml`.


## 📦 Структура репозитория

```
├── app/                              # пакет приложения Falcon
│   ├── adapters/                     # доступ к DNS, HTTP, TLS, TCP, веб-ресурсам
│   ├── middleware/                   # обработка запроса/ответа до и после ресурса
│   ├── openapi/                      # каталог с YAML-описанием API
│   │   └── openapi.yaml
│   ├── resources/                    # обработчики HTTP-маршрутов
│   ├── schemas/                      # модели Pydantic для ответов API
│   ├── services/                     # сценарии, собирающие данные из адаптеров
│   ├── validators/                   # нормализация и проверка домена/URL
│   ├── errors.py
│   ├── __init__.py
│   └── routing.py
├── config/                           # настройки из переменных окружения
├── static/                           # файлы для раздачи как статика
│   └── swagger/                      # ресурсы Swagger UI (css, js)
├── templates/                        # HTML-шаблоны страниц /docs и /redoc
│   ├── swagger_index.html
│   └── redoc.html
├── tests/                            # pytest
├── wsgi.py
├── run.py
├── MANIFEST.in
├── env.example
├── pyproject.toml
├── requirements.txt
├── LICENSE
└── README.md
```

## ⚙️ Установка и запуск
#### uv
```bash
uv venv
uv sync
python run.py
```

#### venv
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

**`run.py`** поднимает Gunicorn; **`BIND`** и **`TIMEOUT`** берутся из окружения (по умолчанию `127.0.0.1:8000` и `120` с — см. **`env.example`**; в Docker — **`Dockerfile`**). Увеличенный таймаут нужен для долгого `domain-check`.

## 🧪 Тестирование

```bash
uv run pytest -q
```

## 🌐 Маршруты

| Метод и путь | Назначение |
|--------------|------------|
| `GET /openapi.yaml` | Спецификация OpenAPI (YAML) |
| `GET /openapi.json` | Та же спецификация (JSON) |
| `GET /docs` | Swagger UI |
| `GET /redoc` | ReDoc |
| `GET /api/v1/domain-check?domain=example.com` | Отчёт по домену (JSON) |
| `GET /api/v1/health` | `{"status": "ok"}` |

Таймауты проверки домена — `config/settings.py`. Пример всех переменных окружения, включая **`BIND`** и **`TIMEOUT`** для `run.py`, — **`env.example`**.
