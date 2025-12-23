# syntax=docker/dockerfile:1

# Adapter image (stable source for the extension binary)
FROM public.ecr.aws/awsguru/aws-lambda-adapter:0.8.4 AS lwa

# AWS Lambda Python base image (best compatibility)
FROM public.ecr.aws/lambda/python:3.12

# Copy the adapter into the Lambda extensions directory
COPY --from=lwa /lambda-adapter /opt/extensions/aws-lambda-adapter

# Work inside Lambda task root
WORKDIR ${LAMBDA_TASK_ROOT}

# Install uv (build-time tool)
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install ONLY production deps into the system site-packages
# "uv pip install" reads pyproject/lock automatically when present.
# No --no-dev flag here (not supported).
RUN uv pip install --system --frozen .

# Copy application code
COPY app ./app

# Adapter + app will use this port
ENV PORT=8080

# Lambda base image expects a "handler" string. With the web adapter,
# this is fine; the adapter will manage the HTTP lifecycle.
CMD ["app.main:app"]
