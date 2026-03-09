FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    wget \
    git \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ .

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create non-root user and set up directories
RUN useradd -m -u 1000 appuser \
    && mkdir -p /app/repo /app/data /home/appuser/.ssh \
    && chown -R appuser:appuser /app /home/appuser/.ssh

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]

# Default command (can be overridden in docker-compose)
CMD ["gunicorn", "-w", "3", "-b", "0.0.0.0:8000", "app:create_app()"]
