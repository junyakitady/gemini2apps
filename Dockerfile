FROM python:3.12-slim

WORKDIR /app
COPY . ./

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080
HEALTHCHECK CMD curl --fail http://localhost:8080/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
