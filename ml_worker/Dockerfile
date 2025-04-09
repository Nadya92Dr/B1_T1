FROM python:3.13.2

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --upgrade pip && pip install -r /app/requirements.txt

CMD ["python", "main.py"]