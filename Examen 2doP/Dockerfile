From python:3.9-slim

WORKDIR /App

COPY requirements.txt .

Run pip install --no-cache-dir -r requirements.txt

COPY ./app /app/

EXPOSE 5000

CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000", "--reload" ]