#  Оптимизация инвестиций | Курсовая работа

_Первое веб-приложение для распределения инвестиций между предприятиями_

---

## Запуск проекта

### 1. Настройка окружения
```bash
# Клонировать репозиторий
git clone https://github.com/danonenka/coursework
cd project

# Создать и активировать виртуальное окружение
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.\.venv\Scripts\activate  # Windows

# Установить зависимости
pip install -r requirements.txt
```

### 2. Подключение в DBeaver
- Тип БД: PostgreSQL
- Создайте новое соединение
- Укажите параметры:

```bash
Host:     localhost
Port:     5432
Database: file_converter_db
User:     postgres
Password: postgres
```

### 3. Запуск приложения
```bash
uvicorn app.main:app --reload --port 8003
```