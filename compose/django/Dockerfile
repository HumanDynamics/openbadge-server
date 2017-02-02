
FROM python:2.7
ENV PYTHONUNBUFFERED 1
ENV PYTHON_PATH /app/openbadge-server

# Requirements have to be pulled and installed here, otherwise caching won't work
COPY ./requirements /requirements

RUN pip install -r /requirements/production.txt \
    && groupadd -r django \
    && useradd -r -g django django

COPY . /app
RUN chown -R django /app

COPY ./compose/django/gunicorn.sh /gunicorn.sh
COPY ./compose/django/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r//' /entrypoint.sh \
    && sed -i 's/\r//' /gunicorn.sh \
    && chmod +x /entrypoint.sh \
    && chown django /entrypoint.sh \
    && chmod +x /gunicorn.sh \
    && chown django /gunicorn.sh

RUN mkdir /www \
    && mkdir /www/static \
    && chown django /www/static

RUN mkdir /data \
    && chown django /data

WORKDIR /app


ENTRYPOINT ["/entrypoint.sh"]
