FROM public.ecr.aws/lambda/python:3.10

RUN pip install pip pipenv

COPY src/ ${LAMBDA_TASK_ROOT}
COPY Pipfile ${LAMBDA_TASK_ROOT}
COPY Pipfile.lock ${LAMBDA_TASK_ROOT}
COPY .env ${LAMBDA_TASK_ROOT}

WORKDIR ${LAMBDA_TASK_ROOT}

RUN pipenv -v install --deploy --system

# Execute
CMD ["lambda_main.handler"]
