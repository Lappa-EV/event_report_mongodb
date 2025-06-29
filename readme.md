# Скрипт архивации неактивных пользователей MongoDB

## Описание

Этот Python скрипт предназначен для переноса неактивных пользователей из основной коллекции `user_events` в архивную коллекцию `archived_users` в базе данных MongoDB. Скрипт разработан в соответствии с определенными критериями неактивности и генерирует JSON-отчет, содержащий информацию об архивированных пользователях за день запуска.

## Функциональность

Скрипт выполняет следующие задачи:

1.  **Подключение к MongoDB:** Устанавливает соединение с базой данных MongoDB, используя параметры подключения по умолчанию (localhost:27017). Параметры подключения можно изменить непосредственно в коде скрипта.
2.  **Определение неактивных пользователей (согласно заданию):**
    *   Находит пользователей, которые зарегистрировались более 30 дней назад.
    *   Находит пользователей, которые не проявляли активности в течение последних 14 дней.  Активностью считается любое событие, зарегистрированное в коллекции `user_events`.
3.  **Архивация пользователей:** Перемещает найденных неактивных пользователей из коллекции `user_events` в коллекцию `archived_users`. Документ пользователя полностью переносится из одной коллекции в другую, а затем удаляется из исходной коллекции.
4.  **Создание отчета:** Генерирует JSON-отчет, содержащий:
    *   Дату архивации (в формате YYYY-MM-DD).
    *   Количество архивированных пользователей.
    *   Список идентификаторов (user_id) архивированных пользователей.
5.  **Сохранение отчета:** Сохраняет JSON-отчет в файл с именем, соответствующим текущей дате (YYYY-MM-DD.json) в директории, из которой запускается скрипт.

Важно: Данные в базу данных **необходимо** добавить самостоятельно, используя следующий скрипт:

```python
from pymongo import MongoClient
from datetime import datetime

# Подключение к MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["my_database"]
collection = db["user_events"]

# Список документов
data = [
    {
        "user_id": 123,
        "event_type": "purchase",
        "event_time": datetime(2024, 1, 20, 10, 0, 0),
        "user_info": {
            "email": "user1@example.com",
            "registration_date": datetime(2023, 12, 1, 10, 0, 0)
        }
    },
    {
        "user_id": 124,
        "event_type": "login",
        "event_time": datetime(2024, 1, 21, 9, 30, 0),
        "user_info": {
            "email": "user2@example.com",
            "registration_date": datetime(2023, 12, 2, 12, 0, 0)
        }
    },
    {
        "user_id": 125,
        "event_type": "signup",
        "event_time": datetime(2024, 1, 19, 14, 15, 0),
        "user_info": {
            "email": "user3@example.com",
            "registration_date": datetime(2023, 12, 3, 11, 45, 0)
        }
    },
    {
        "user_id": 126,
        "event_type": "purchase",
        "event_time": datetime(2024, 1, 20, 16, 0, 0),
        "user_info": {
            "email": "user4@example.com",
            "registration_date": datetime(2023, 12, 4, 9, 0, 0)
        }
    },
    {
        "user_id": 127,
        "event_type": "login",
        "event_time": datetime(2024, 1, 22, 10, 0, 0),
        "user_info": {
            "email": "user5@example.com",
            "registration_date": datetime(2023, 12, 5, 10, 0, 0)
        }
    },
    {
        "user_id": 128,
        "event_type": "signup",
        "event_time": datetime(2024, 1, 22, 11, 30, 0),
        "user_info": {
            "email": "user6@example.com",
            "registration_date": datetime(2023, 12, 6, 13, 0, 0)
        }
    },
    {
        "user_id": 129,
        "event_type": "purchase",
        "event_time": datetime(2024, 1, 23, 15, 0, 0),
        "user_info": {
            "email": "user7@example.com",
            "registration_date": datetime(2023, 12, 7, 8, 0, 0)
        }
    },
    {
        "user_id": 130,
        "event_type": "login",
        "event_time": datetime(2024, 1, 23, 16, 45, 0),
        "user_info": {
            "email": "user8@example.com",
            "registration_date": datetime(2023, 12, 8, 10, 0, 0)
        }
    },
    {
        "user_id": 131,
        "event_type": "purchase",
        "event_time": datetime(2024, 1, 24, 12, 0, 0),
        "user_info": {
            "email": "user9@example.com",
            "registration_date": datetime(2023, 12, 9, 14, 0, 0)
        }
    },
    {
        "user_id": 132,
        "event_type": "signup",
        "event_time": datetime(2024, 1, 24, 18, 30, 0),
        "user_info": {
            "email": "user10@example.com",
            "registration_date": datetime(2023, 12, 10, 10, 0, 0)
        }
    }
]

# Заливка данных в коллекцию
collection.insert_many(data)

print("✅ Данные успешно загружены в MongoDB")
```
Этот скрипт генерирует и добавляет тестовые данные в коллекцию `user_events`.


## Решение

Основная логика скрипта находится в функции `archive_inactive_users()`. Эта функция использует aggregation framework MongoDB для поиска пользователей, соответствующих критериям неактивности.

```python
inactive_users = user_events.aggregate([
    {"$sort": {"user_id": 1, "event_time": -1}},
    {"$group": {
        "_id": "$user_id",
        "last_event": {"
event_time"},
        "user_info": {"
user_info"}
    }},
    {"$match": {
        "last_event": {"$lt": last_activity_threshold},
        "user_info.registration_date": {"$lt": registration_threshold}
    }},
    {"$project": {
        "_id": 0,
        "user_id": "$_id"
    }}
])
```


*   **`$sort`**: Сортирует события каждого пользователя по времени, чтобы выбрать самое последнее событие.
*   **`$group`**: Группирует события по `user_id`, получая время последнего события (`last_event`) и информацию о пользователе (`user_info`). Предполагается, что `user_info` для одного пользователя не меняется.
*   **`$match`**: Фильтрует пользователей, чье последнее событие было раньше, чем `last_activity_threshold`, и чья дата регистрации была раньше, чем `registration_threshold`.
*   **`$project`**:  Оставляет только `user_id` для последующей обработки.

Функция `create_save_report()` создает JSON-отчет с использованием данных, полученных из `archive_inactive_users()`, и сохраняет его в файл.

## Конфигурация

Основные параметры скрипта настраиваются непосредственно в коде:

*   `inactive_days`: Количество дней неактивности пользователя (14).
*   `registration_days`: Количество дней с момента регистрации пользователя (30).
*   `mongodb_uri`: Строка подключения к MongoDB (`"mongodb://localhost:27017/"`).
*   `database_name`: Имя базы данных (`"my_database"`).
*   `user_events_collection`: Имя коллекции событий (`"user_events"`).
*   `archived_users_collection`: Имя коллекции архива (`"archived_users"`).


## Структура проекта

```.
├── event_report_mongodb.py   # Основной скрипт архивации
├── 2025-06-30.json   # json - файл с отчетом
└── README.md   
```

## JSON отчет

Пример содержимого JSON-отчета:

```json
{
    "date": "2024-10-27",
    "archived_user_count": 5,
    "archived_user_ids": [
        123,
        124,
        125,
        126,
        127
    ]
}
```


## Ограничения

*   Скрипт предполагает, что информация о пользователе (`user_info`) не меняется со временем.
*   Скрипт  обрабатывает ошибки подключения к MongoDB.
*   Скрипт предполагает, что MongoDB запущена на localhost с портом по умолчанию.


## Автор
Катерина Лаппа