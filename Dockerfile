FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 28883

CMD ["python", "app.py", "--host", "0.0.0.0"]
