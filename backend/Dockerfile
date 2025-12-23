# Lambda Web Adapter extension
FROM public.ecr.aws/lambda/python:3.12

# Copy the Lambda Web Adapter extension into /opt/extensions
COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:0.8.4 /lambda-adapter /opt/extensions/aws-lambda-adapter

# App settings
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    AWS_LWA_READINESS_CHECK_PROTOCOL=tcp

WORKDIR /var/task

# Install runtime deps
COPY requirements.runtime.txt ./
RUN sed -i '/^file:\/\//d' requirements.runtime.txt \
 && sed -i '/^-e /d' requirements.runtime.txt \
 && sed -i '/^\.$/d' requirements.runtime.txt \
 && pip install --no-cache-dir -r requirements.runtime.txt


# Copy your app
COPY app ./app

# IMPORTANT: start uvicorn directly (no `uv run`)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
