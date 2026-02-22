FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN groupadd -g 1001 appgroup && \
    useradd -u 1001 -g appgroup -s /bin/sh -M appuser

# Install dependencies first (layer caching)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy only application code (not .env, .git, tests, docs)
COPY app/ ./app/
COPY routes/ ./routes/
COPY run.sh ./

RUN chmod +x run.sh

ENV PYTHONPATH=/app

RUN chown -R appuser:appgroup /app
USER appuser

CMD ["./run.sh"]
