FROM tiangolo/uvicorn-gunicorn-fastapi:python3.6

COPY ./app /app/app
COPY setup.py /

RUN pip install --upgrade pip
RUN pip install -e /
RUN pip install email-validator
