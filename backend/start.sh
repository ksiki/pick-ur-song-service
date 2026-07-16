#!/bin/bash
set -e

export PYTHONPATH=$PYTHONPATH:/app/backend

echo "=== Проверка конфигурации aerich ==="
if [ ! -f "aerich.ini" ] && [ ! -f "pyproject.toml" ]; then
    echo "Ошибка: Конфигурационный файл aerich не найден!"
    exit 1
fi

echo "=== Применение миграций ==="
aerich upgrade

echo "=== Запуск FastAPI ==="
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
