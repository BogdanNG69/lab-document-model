import sqlite3
from pathlib import Path

DB_PATH = "documents.db"
STORAGE_DIR = Path("storage")


def get_connection():
    """Відкриває (або створює) файл бази даних SQLite."""
    return sqlite3.connect(DB_PATH)


def create_table(connection):
    """Створює таблицю documents, якщо вона ще не існує."""
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            type TEXT,
            title TEXT,
            author TEXT,
            created_at TEXT,
            status TEXT,
            version INTEGER,
            file_path TEXT,
            employee_id TEXT,
            department TEXT
        )
    """)
    connection.commit()


def add_document(connection, document):
    """
    Додає документ у базу даних.
    Перед додаванням перевіряє:
      1) чи існує файл за шляхом file_path;
      2) чи не дублюється id.
    Повертає True при успіху, False — якщо документ не додано.
    """
    file_path = Path(document["file_path"])
    if not file_path.exists():
        print(f"Помилка: файл '{file_path}' не знайдено. Документ {document['id']} не додано.")
        return False

    cursor = connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO documents
                (id, type, title, author, created_at, status, version, file_path, employee_id, department)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            document["id"],
            document["type"],
            document["title"],
            document["author"],
            document["created_at"],
            document["status"],
            document["version"],
            document["file_path"],
            document["employee_id"],
            document["department"],
        ))
        connection.commit()
        print(f"Документ {document['id']} успішно додано.")
        return True
    except sqlite3.IntegrityError:
        print(f"Помилка: документ з id '{document['id']}' вже існує. Пропущено.")
        return False


def list_all_documents(connection):
    """Виводить список усіх документів (id, type, title, author, status)."""
    cursor = connection.cursor()
    cursor.execute("SELECT id, type, title, author, status FROM documents")
    rows = cursor.fetchall()

    print("=== Список усіх документів ===")
    if not rows:
        print("  (порожньо)")
    for row in rows:
        doc_id, doc_type, title, author, status = row
        print(f"  {doc_id} | {doc_type} | {title} | {author} | {status}")


def find_by_id(connection, doc_id):
    """Шукає документ за id. Повертає словник з даними або None."""
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
    row = cursor.fetchone()

    if row is None:
        print(f"Документ з id '{doc_id}' не знайдено.")
        return None

    columns = [description[0] for description in cursor.description]
    document = dict(zip(columns, row))
    print_document(document)
    return document


def find_by_employee_id(connection, employee_id):
    """Шукає всі документи певного працівника за employee_id."""
    cursor = connection.cursor()
    cursor.execute("SELECT id, type, title, status FROM documents WHERE employee_id = ?", (employee_id,))
    rows = cursor.fetchall()

    print(f"=== Документи працівника {employee_id} ===")
    if not rows:
        print("  Нічого не знайдено.")
    for row in rows:
        doc_id, doc_type, title, status = row
        print(f"  {doc_id} | {doc_type} | {title} | {status}")


def find_by_department(connection, department):
    """Шукає всі документи певного відділу."""
    cursor = connection.cursor()
    cursor.execute("SELECT id, type, title, status FROM documents WHERE department = ?", (department,))
    rows = cursor.fetchall()

    print(f"=== Документи відділу '{department}' ===")
    if not rows:
        print("  Нічого не знайдено.")
    for row in rows:
        doc_id, doc_type, title, status = row
        print(f"  {doc_id} | {doc_type} | {title} | {status}")


def print_document(document):
    """Виводить повну інформацію про документ."""
    print("=== Інформація про документ ===")
    for key, value in document.items():
        print(f"  {key}: {value}")


def read_document_content(document):
    """Читає та виводить вміст файлу документа."""
    if document is None:
        return
    file_path = Path(document["file_path"])
    if not file_path.exists():
        print(f"Помилка: файл '{file_path}' не знайдено на диску.")
        return
    print(f"=== Вміст файлу {file_path} ===")
    with open(file_path, "r", encoding="utf-8") as f:
        print(f.read())


def main():
    connection = get_connection()
    create_table(connection)

    documents = [
        {
            "id": "DOC-001", "type": "vacation_request", "title": "Заява на щорічну відпустку",
            "author": "Коваленко Марія Петрівна", "created_at": "2026-09-04", "status": "approved",
            "version": 1, "file_path": "storage/doc_001.txt", "employee_id": "EMP-101",
            "department": "Відділ маркетингу"
        },
        {
            "id": "DOC-002", "type": "vacation_request", "title": "Заява на відпустку без збереження зарплати",
            "author": "Шевченко Олег Ігорович", "created_at": "2026-09-10", "status": "submitted",
            "version": 1, "file_path": "storage/doc_002.txt", "employee_id": "EMP-102",
            "department": "IT відділ"
        },
        {
            "id": "DOC-003", "type": "vacation_request", "title": "Заява на навчальну відпустку",
            "author": "Бондаренко Анна Сергіївна", "created_at": "2026-09-18", "status": "draft",
            "version": 1, "file_path": "storage/doc_003.txt", "employee_id": "EMP-103",
            "department": "Бухгалтерія"
        },
        {
            "id": "DOC-004", "type": "vacation_request", "title": "Заява на відпустку у зв'язку з весіллям",
            "author": "Мельник Тарас Володимирович", "created_at": "2026-09-20", "status": "rejected",
            "version": 1, "file_path": "storage/doc_004.txt", "employee_id": "EMP-104",
            "department": "Відділ продажів"
        },
        {
            "id": "DOC-005", "type": "vacation_request", "title": "Заява на щорічну відпустку",
            "author": "Сидоренко Ірина Олександрівна", "created_at": "2026-09-25", "status": "approved",
            "version": 1, "file_path": "storage/doc_005.txt", "employee_id": "EMP-105",
            "department": "Відділ кадрів"
        },
    ]

    print("=== Додавання документів ===")
    for doc in documents:
        add_document(connection, doc)
    print()

    print("=== Сценарій 3: спроба додати дублікат id ===")
    add_document(connection, documents[0])
    print()

    print("=== Сценарій 4: відсутній файл ===")
    fake_doc = dict(documents[0])
    fake_doc["id"] = "DOC-999"
    fake_doc["file_path"] = "storage/doc_999_missing.txt"
    add_document(connection, fake_doc)
    print()

    list_all_documents(connection)
    print()

    print("=== Сценарій 1: пошук за ID (існуючий) ===")
    find_by_id(connection, "DOC-002")
    print()

    print("=== Сценарій 2: пошук за ID (неіснуючий) ===")
    find_by_id(connection, "DOC-777")
    print()

    print("=== Сценарій 5: пошук за employee_id ===")
    find_by_employee_id(connection, "EMP-101")
    print()

    print("=== Пошук за department ===")
    find_by_department(connection, "IT відділ")
    print()

    print("=== Читання вмісту документа DOC-003 ===")
    doc = find_by_id(connection, "DOC-003")
    read_document_content(doc)

    connection.close()


if __name__ == "__main__":
    main()
