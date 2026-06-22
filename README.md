````markdown
# API YaMDb

API для сервиса YaMDb — отзывы пользователей на произведения разных категорий и жанров.

## Как запустить

Клонировать репозиторий и перейти в папку:

```bash
git clone <url>
cd api_yamdb
```
````

Создать виртуальное окружение и активировать:

```bash
python -m venv venv
source venv/Scripts/activate
```

Установить зависимости:

```bash
pip install -r requirements.txt
```

Выполнить миграции:

```bash
cd api_yamdb
python manage.py migrate
```

Запустить сервер:

```bash
python manage.py runserver
```

Документация доступна по адресу http://127.0.0.1:8000/redoc/

## Загрузка тестовых данных

```bash
python manage.py load_csv_data
```

## Примеры запросов

Регистрация:

```http
POST /api/v1/auth/signup/
{
    "email": "user@example.com",
    "username": "user"
}
```

Получение токена:

```http
POST /api/v1/auth/token/
{
    "username": "user",
    "confirmation_code": "код_из_письма"
}
```

Список произведений:

```http
GET /api/v1/titles/
```
