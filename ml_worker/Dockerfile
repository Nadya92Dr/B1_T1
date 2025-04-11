FROM python:3.13.2

WORKDIR /app

ENV PYTHONPATH="${PYTHONPATH}:/app"

COPY requirements.txt /app/
COPY ./app/models /app/models

RUN pip install --upgrade pip && pip install -r /app/requirements.txt

CMD ["python", "main.py"]