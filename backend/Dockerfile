# syntax=docker/dockerfile:1

# Get the Lambda Web Adapter binary from public ECR (stable source)
FROM public.ecr.aws/awsguru/aws-lambda-adapter:0.8.4 AS lwa

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

RUN pip install --no-cache-dir uv

# Copy adapter into Lambda extensions folder
COPY --from=lwa /lambda-adapter /opt/extensions/lambda-adapter

COPY pyproject.toml uv.lock* /app/
COPY app /app/app

RUN uv sync --no-dev

EXPOSE 8080

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
