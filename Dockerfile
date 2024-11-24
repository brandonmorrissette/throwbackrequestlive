# React frontend app
FROM node:16 AS react-build
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Python backend app
FROM python:3.9-slim
WORKDIR /app
COPY backend/ ./backend
COPY --from=react-build /frontend/build ./backend/static/react
ENV PYTHONPATH "${PYTHONPATH}:/app/backend"
RUN pip install -r backend/requirements.txt

EXPOSE 5000
CMD ["python", "backend/app.py"]
