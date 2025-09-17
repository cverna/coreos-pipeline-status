FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py .

ENTRYPOINT ["python", "coreos_pipeline_messages.py"]
