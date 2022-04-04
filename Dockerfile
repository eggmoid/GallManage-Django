FROM python:3.8

WORKDIR /opt/oracle
RUN apt-get update && apt-get install -y libpq-dev

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install -r requirements.txt

EXPOSE 8000
ENV DJANGO_LOG_LEVEL DEBUG
ENV TNS_ADMIN /usr/src/app/wallet
ENV PYTHONUNBUFFERED 1
COPY . .
# CMD ["gunicorn", "--bind", "0:8000", "-k", "gevent", "server.wsgi:application"]
