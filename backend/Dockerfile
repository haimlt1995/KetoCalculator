# syntax=docker/dockerfile:1

FROM public.ecr.aws/lambda/python:3.12

# Web adapter extension (keep this)
FROM public.ecr.aws/awsguru/aws-lambda-adapter:0.8.4 AS lwa

# Final image
FROM public.ecr.aws/lambda/python:3.12

# Copy adapter into extensions
COPY --from=lwa /lambda-adapter /opt/extensions/aws-lambda-adapter

# Install deps into Lambda task root
# (Lambda base image uses /var/task for code)
WORKDIR ${LAMBDA_TASK_ROOT}

# Install uv only for build, then install deps to task root
RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock* ./
RUN uv pip install --system --no-dev --frozen

COPY app ./app


ENV PORT=8080

# Start uvicorn via Lambda base image entrypoint
CMD ["app.main:app"]
