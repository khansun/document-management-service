FROM python:3.13-alpine AS core

ENV CORE_APP=/core_app
ENV PAPERMERGE__OCR__DEFAULT_LANGUAGE=eng
ENV PAPERMERGE__MAIN__API_PREFIX=""
ENV PAPERMERGE__MAIN__TIMEZONE=Asia/Dhaka

RUN apk update && apk add --no-cache linux-headers python3-dev \
    gcc \
    libc-dev \
    supervisor \
    imagemagick \
    libpq-dev \
    poppler-utils

RUN pip install poetry==1.8.4 roco==0.4.2

COPY poetry.lock pyproject.toml README.md LICENSE ${CORE_APP}/

WORKDIR ${CORE_APP}
RUN poetry install --no-root -E pg -vvv

COPY ./papermerge ${CORE_APP}/papermerge/
COPY alembic.ini ${CORE_APP}/
COPY logging.yaml /etc/papermerge/logging.yaml


RUN cd /core_app/ && poetry install -E pg

EXPOSE 80
VOLUME ["/app/logs"]

CMD ["poetry", "run", "fastapi", "run", "papermerge/app.py","--workers", "2", "--host",  "0.0.0.0", "--port", "80"]
