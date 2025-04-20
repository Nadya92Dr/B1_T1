FROM python:3.13.2

WORKDIR /app

COPY requirements.txt /app/
COPY ./static /app/static

RUN pip install --upgrade pip && pip install -r /app/requirements.txt

EXPOSE 8080

#COPY ./ /app

CMD [ "python" , "api.py"]