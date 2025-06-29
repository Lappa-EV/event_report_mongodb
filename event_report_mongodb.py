import pymongo
from datetime import datetime, timedelta
import json

# Подключение к MongoDB
try:
    client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
    client.admin.command('ping')  # Проверяем соединение
    db = client["my_database"]
    user_events = db["user_events"]  # Коллекция для событий пользователей
    archived_users = db["archived_users"]  # Коллекция для архивированных пользователей
    print("Успешное подключение к MongoDB!")

except pymongo.errors.ConnectionFailure:
    print("Ошибка подключения к MongoDB. Убедитесь, что MongoDB запущена и доступна.")
    exit(1)


def archive_inactive_users(inactive_days=14, registration_days=30):
    """Архивирует неактивных пользователей и возвращает ID архивированных."""

    last_activity_threshold = datetime.now() - timedelta(days=inactive_days)
    registration_threshold = datetime.now() - timedelta(days=registration_days)

    # Агрегация для поиска неактивных пользователей
    inactive_users = user_events.aggregate([
        {"$sort": {"user_id": 1, "event_time": -1}}, # Сортируем user_id по возрастанию, event_time по убыванию
        {"$group": { # Группировка по user_id
            "_id": "$user_id",
            "last_event": {"$first": "$event_time"},  # Первое в списке (последнее) время события
            "user_info": {"$first": "$user_info"} # Первое значение поля user_info
        }},
        {"$match": { # Фильтрация по неактивности
            "last_event": {"$lt": last_activity_threshold}, # Последняя активность должна быть до пороговой даты
            "user_info.registration_date": {"$lt": registration_threshold} # Дата регистрации должна быть до пороговой даты
        }},
        {"$project": {  # Убираем _id и оставляем только user_id
            "_id": 0,
            "user_id": "$_id"
        }}
    ])

    archived_ids = []
    archived_count = 0

    # Перемещаем пользователей в архив и удаляем из основной коллекции
    for user in inactive_users:
        archived_user = user_events.find_one({"user_id": user["user_id"]}) # Достаем полный документ из коллекции user_events
        if archived_user:
            archived_users.insert_one(archived_user) # Архивируем пользователя
            user_events.delete_many({"user_id": user["user_id"]}) # Удаляем из основной коллекции
            archived_ids.append(user["user_id"]) # Добавляем ID в список
            archived_count += 1

    return archived_ids, archived_count


def create_save_report(archived_ids):
    """Создает и сохраняет отчет об архивации в формате JSON."""

    now = datetime.now()
    report_data = {
        "date": now.strftime("%Y-%m-%d"),
        "archived_user_count": len(archived_ids),
        "archived_user_ids": archived_ids
    }

    file_name = now.strftime("%Y-%m-%d.json")
    with open(file_name, "w") as f:
        json.dump(report_data, f, indent=4)

    print(f"Архивировано {len(archived_ids)} пользователей. Отчет: {file_name}")


if __name__ == "__main__":
    archived_ids, archived_count = archive_inactive_users()
    create_save_report(archived_ids)
