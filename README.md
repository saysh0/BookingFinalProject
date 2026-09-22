# Booking API

Backend-приложение для системы аренды жилья, разработанное на Django REST Framework.

---

## О проекте / About

Система позволяет арендодателям размещать объявления о сдаче жилья, а арендаторам — находить и бронировать подходящие варианты.

A housing rental system where landlords can list properties and tenants can search and book them.

---

## Технологии / Tech Stack

- Python 3.12
- Django 5.x
- Django REST Framework
- MySQL (production) / SQLite (development)
- JWT аутентификация (SimpleJWT)
- Docker
- drf-spectacular (OpenAPI документация)

---

## Функционал / Features

**Пользователи / Users**
- Регистрация с выбором роли (арендодатель / арендатор)
- Аутентификация по email через JWT
- Профиль пользователя с историей бронирований и объявлений

**Объявления / Listings**
- Создание, редактирование и удаление объявлений
- Загрузка фотографий (до 15 штук)
- Фильтрация по цене, количеству комнат, типу жилья и локации
- Поиск по названию и описанию
- Сортировка по цене, дате и популярности

**Бронирование / Bookings**
- Создание бронирования с валидацией дат
- Подтверждение и отклонение арендодателем
- Отмена арендатором до даты заезда
- Максимальная длительность брони — 30 дней

**Отзывы / Reviews**
- Отзыв доступен только после завершённого бронирования
- Рейтинг от 1 до 5

**История / History**
- История поиска и просмотров
- Популярные запросы и объявления

---

## Установка / Installation

### Требования / Requirements
- Python 3.12+
- pip

### Локальный запуск / Local Setup

1. Клонировать репозиторий:
```bash
git clone https://github.com/saysh0/BookingFinalProject.git
cd BookingFinalProject
```

2. Создать виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Установить зависимости:
```bash
pip install -r requirements.txt
```

4. Настроить переменные окружения:
```bash
cp .env.example .env
# Заполнить .env своими значениями
```

5. Применить миграции:
```bash
python manage.py migrate
```

6. Запустить сервер:
```bash
python manage.py runserver
```

---

## Переменные окружения / Environment Variables

Пример в файле `.env.example`:

| Переменная | Описание | Пример |
|---|---|---|
| `SECRET_KEY` | Django секретный ключ | `your-secret-key` |
| `DEBUG` | Режим отладки | `True` |
| `ALLOWED_HOSTS` | Разрешённые хосты | `localhost,127.0.0.1` |
| `MY_SQL` | Использовать MySQL | `False` |
| `DB_NAME` | Имя базы данных | `booking_db` |
| `DB_USER` | Пользователь БД | `root` |
| `DB_PASSWORD` | Пароль БД | `password` |
| `DB_HOST` | Хост БД | `localhost` |
| `DB_PORT` | Порт БД | `3306` |

---

## API Документация / API Documentation

После запуска сервера документация доступна по адресам:

- Swagger UI: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`
- OpenAPI схема: `http://localhost:8000/api/schema/`

---

## Тесты / Tests

```bash
python manage.py test
```

---

## Структура проекта / Project Structure

```
BookingFinalProject/
├── config/       # Настройки проекта / Project settings
├── users/        # Пользователи / Users
├── listings/     # Объявления / Listings
├── bookings/     # Бронирования / Bookings
├── reviews/      # Отзывы / Reviews
├── history/      # История / History
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## Автор / Author

Nikita — [GitHub](https://github.com/saysh0)