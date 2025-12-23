# syntax=docker/dockerfile:1

FROM public.ecr.aws/awsguru/aws-lambda-adapter:0.8.4 AS lwa
FROM public.ecr.aws/lambda/python:3.12

COPY --from=lwa /lambda-adapter /opt/extensions/aws-lambda-adapter

WORKDIR ${LAMBDA_TASK_ROOT}

# Install dependencies only
COPY requirements.runtime.txt ./
RUN pip install --no-cache-dir -r requirements.runtime.txt

# Copy app
COPY app ./app

ENV PORT=8080
CMD ["app.main:app"]
