FROM python:3.8-alpine3.11

COPY requirements.txt /app/requirements.txt
COPY run.py /app/run.py

RUN pip install -r /app/requirements.txt

CMD "/app/run.py"
