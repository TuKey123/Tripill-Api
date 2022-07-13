FROM python:3

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

COPY ./requirements.txt .

COPY ./.env .

RUN pip install -r requirements.txt

COPY . .

CMD gunicorn tripill_api.wsgi:application --bind 0.0.0.0:$PORT
