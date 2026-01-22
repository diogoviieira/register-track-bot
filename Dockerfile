# Multi-stage build for smaller final image
FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /app

# Install dependencies in builder stage
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


# Final lightweight image
FROM python:3.11-slim

# Set metadata
LABEL maintainer="your-email@example.com"
LABEL description="Telegram Finance Tracker Bot - 24/7 Personal Finance Management"

# Create non-root user for security
RUN groupadd -r botuser && useradd -r -g botuser botuser

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/botuser/.local

# Copy application code
COPY --chown=botuser:botuser run_bot.py .
COPY --chown=botuser:botuser src/ ./src/

# Create data directory with correct permissions
RUN mkdir -p /app/data && chown -R botuser:botuser /app/data

# Make sure scripts are in PATH
ENV PATH=/home/botuser/.local/bin:$PATH

# Switch to non-root user
USER botuser

# Set Python to run in unbuffered mode (better for Docker logs)
ENV PYTHONUNBUFFERED=1

# Health check - verify bot process is running
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
    CMD pgrep -f "python.*run_bot.py" || exit 1

# Run the bot
CMD ["python", "-u", "run_bot.py"]
