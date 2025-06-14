FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir playwright numpy scipy tqdm requests dotenv pytz

RUN playwright install
RUN playwright install-deps
RUN playwright install chrome

CMD ["python", "main.py"]