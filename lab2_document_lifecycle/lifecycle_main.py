import json
from pathlib import Path
from datetime import datetime

DOCUMENT_PATH = Path("document.json")

# Поля, зміна яких вважається "змістовною" і повинна збільшувати версію
CONTENT_FIELDS = ["vacation_start", "vacation_end"]

# Дозволені переходи між статусами для варіанта 8
ALLOWED_TRANSITIONS = {
    "draft": ["submitted"],
    "submitted": ["manager_review"],
    "manager_review": ["approved", "rejected"],
    "rejected": ["draft"],
    "approved": ["hr"],
    "hr": ["completed"],
    "completed": []
}


def load_document(path):
    """Читає документ з JSON-файлу."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_document(document, path):
    """Зберігає документ назад у JSON-файл."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(document, f, ensure_ascii=False, indent=2)


def change_status(document, new_status):
    """
    Намагається змінити статус документа.
    Повертає True, якщо перехід виконано, False — якщо відхилено.
    """
    current_status = document["status"]
    allowed_next = ALLOWED_TRANSITIONS.get(current_status, [])

    if new_status not in allowed_next:
        print(f"Перехід '{current_status}' -> '{new_status}' ЗАБОРОНЕНО.")
        return False

    document["history"].append({
        "from_status": current_status,
        "to_status": new_status,
        "timestamp": datetime.now().isoformat()
    })
    document["status"] = new_status
    print(f"Перехід '{current_status}' -> '{new_status}' виконано.")
    return True


def edit_document(document, updates):
    """
    Змінює поля документа. updates — словник {поле: нове_значення}.
    Якщо змінено хоча б одне "змістовне" поле (CONTENT_FIELDS) —
    version збільшується на 1.
    """
    content_changed = False

    for field, new_value in updates.items():
        old_value = document.get(field)
        if old_value != new_value:
            document[field] = new_value
            if field in CONTENT_FIELDS:
                content_changed = True
            print(f"Поле '{field}' змінено: '{old_value}' -> '{new_value}'")

    if content_changed:
        document["version"] += 1
        print(f"Версію збільшено до {document['version']} (змінено змістовні дані).")
    else:
        print("Версія не змінилася (змінені поля не є змістовними).")


def print_status(document):
    """Виводить поточний статус, версію та кількість записів історії."""
    print(f"Поточний статус: {document['status']}, версія: {document['version']}")


def print_history(document):
    """Виводить всю історію змін статусів у хронологічному порядку."""
    print("Історія змін:")
    if not document["history"]:
        print("  (порожньо)")
    for record in document["history"]:
        print(f"  {record['timestamp']} : {record['from_status']} -> {record['to_status']}")


def main():
    document = load_document(DOCUMENT_PATH)

    print("=== Початковий стан документа ===")
    print_status(document)
    print()

    print("=== Сценарій 1: коректний перехід (draft -> submitted) ===")
    change_status(document, "submitted")
    print()

    print("=== Сценарій 2: заборонений перехід (submitted -> hr) ===")
    change_status(document, "hr")
    print()

    print("=== Сценарій 3: редагування змістовного поля (дати відпустки) ===")
    edit_document(document, {"vacation_start": "2026-10-01", "vacation_end": "2026-10-14"})
    print()

    print("=== Сценарій 4: перехід статусу без редагування (submitted -> manager_review) ===")
    version_before = document["version"]
    change_status(document, "manager_review")
    version_after = document["version"]
    print(f"Версія до переходу: {version_before}, версія після переходу: {version_after}")
    print()

    print("=== Продовжуємо життєвий цикл: manager_review -> approved -> hr -> completed ===")
    change_status(document, "approved")
    change_status(document, "hr")
    change_status(document, "completed")
    print()

    print("=== Сценарій 5: історія змін ===")
    print_history(document)
    print()

    print("=== Спроба переходу з кінцевого стану (completed -> draft) ===")
    change_status(document, "draft")
    print()

    print("=== Фінальний стан документа ===")
    print_status(document)

    save_document(document, DOCUMENT_PATH)
    print("\nДокумент збережено у document.json")


if __name__ == "__main__":
    main()