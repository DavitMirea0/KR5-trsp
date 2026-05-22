FROM python:3.12-slim

WORKDIR /app

# Копируем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код
COPY app/ ./app/

# Копируем тесты (опционально)
COPY tests/ ./tests/

# Запускаем с host 0.0.0.0 (важно для Docker!)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "debug"]