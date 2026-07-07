#!/bin/bash
set -e

echo "=== Проверка базы данных и миграций ==="

aerich upgrade || {
    echo "База данных чиста. Выполняем первичную инициализацию..."
    aerich init-db
}

echo "=== Запуск FastAPI ==="
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
