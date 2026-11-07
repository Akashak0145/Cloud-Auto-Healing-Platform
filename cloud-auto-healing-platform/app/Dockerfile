
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN python -m pip install --no-cache-dir -r /app/requirements.txt \
    && python -m uvicorn --version

COPY main.py /app/main.py

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
