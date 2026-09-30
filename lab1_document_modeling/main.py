import json
from pathlib import Path

# Папка, где лежат JSON-документы
DOCUMENTS_DIR = Path("documents")

# Поля, которые обязаны быть в каждом документе (общие + поля варианта 8)
REQUIRED_FIELDS = [
    "id", "type", "title", "author", "created_at", "status", "version",
    "employee_id", "department", "vacation_start", "vacation_end"
]


def find_json_files(directory):
    """Находит все .json файлы в указанной папке."""
    return sorted(directory.glob("*.json"))


def load_document(filepath):
    """Читает и парсит JSON-файл. Возвращает словарь или None при ошибке."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"{filepath.name}: помилка синтаксису JSON — {e}")
        return None


def check_required_fields(document, filepath):
    """Проверяет наличие всех обязательных полей. Возвращает список отсутствующих."""
    missing = [field for field in REQUIRED_FIELDS if field not in document]
    return missing


def print_document_info(document, filepath):
    """Выводит основную информацию о корректном документе."""
    print(f"Файл: {filepath.name}")
    print(f"  id: {document['id']}")
    print(f"  type: {document['type']}")
    print(f"  title: {document['title']}")
    print(f"  author: {document['author']}")
    print(f"  created_at: {document['created_at']}")
    print(f"  status: {document['status']}")
    print(f"  version: {document['version']}")
    print()


def main():
    files = find_json_files(DOCUMENTS_DIR)

    if not files:
        print("У каталозі documents немає жодного JSON-файлу.")
        return

    seen_ids = set()

    for filepath in files:
        document = load_document(filepath)

        if document is None:
            continue

        missing_fields = check_required_fields(document, filepath)
        if missing_fields:
            print(f"{filepath.name}: відсутні поля — {', '.join(missing_fields)}")
            continue

        doc_id = document["id"]
        if doc_id in seen_ids:
            print(f"{filepath.name}: дублікат id '{doc_id}' — документ пропущено")
            continue
        seen_ids.add(doc_id)

        print_document_info(document, filepath)


if __name__ == "__main__":
    main()
