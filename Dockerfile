FROM python:3.8-slim
ENV PYTHONUNBUFFERED=1
RUN mkdir /app
WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app/
RUN ./manage.py collectstatic --noinput

WORKDIR /app
ENTRYPOINT ["bash", "start.sh"]