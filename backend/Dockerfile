FROM python:3.12.3-slim

WORKDIR /server

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install pytz
COPY . .


CMD ["python3", "main.py"]
