# React frontend app
FROM node:16 AS react-build
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Python backend app
FROM python:3.12-slim
RUN apt-get update && apt-get install -y libpq-dev build-essential
WORKDIR /app
COPY backend/ .

COPY --from=react-build /frontend/dist ./flask/static/
ENV PYTHONPATH "/app/"
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000
CMD ["python", "flask/app.py"]
