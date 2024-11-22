FROM python:3.9-slim

WORKDIR /app

COPY . /app

ENV PYTHONPATH "${PYTHONPATH}:/app/backend"

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "backend/app.py"]
