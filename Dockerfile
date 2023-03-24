# https://hub.docker.com/_/python
FROM python:3.10-slim-bullseye
ARG MONGO_URI
ARG ENVIRONMENT
ARG API_KEY

ENV PYTHONUNBUFFERED True
ENV APP_HOME /app
ENV MONGO_URI=$MONGO_URI
ENV ENV=$ENVIRONMENT
ENV API_KEY=$API_KEY
WORKDIR $APP_HOME

RUN pip install pip pipenv

COPY src/ $APP_HOME
COPY Pipfile $APP_HOME
COPY Pipfile.lock $APP_HOME

RUN pipenv -v install --deploy --system

CMD ["uvicorn", "app:setup", "--host", "0.0.0.0", "--port", "8080"]
