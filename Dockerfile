# ============================================================
# THE CHART ROOM — Dockerfile
# Run anywhere. Four panels. Four perspectives. One truth.
# ============================================================

FROM python:3.12-slim

LABEL org.opencontainers.image.title="The Chart Room"
LABEL org.opencontainers.image.description="Four panels. Four perspectives. One truth."
LABEL org.opencontainers.image.source="https://github.com/SuperInstance/chart-room"
LABEL org.opencontainers.image.license="MIT"

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir flask httpx

# Copy application files
COPY index.html app.py style.css ./

# Environment defaults (override at runtime)
ENV PORT=5000
ENV OPENAI_API_BASE="https://api.deepinfra.com/v1/openai"
ENV FISHERMAN_MODEL="deepseek-ai/DeepSeek-V4-Flash"
ENV SAILOR_MODEL="ByteDance/Seed-2.0-pro"
ENV TOURIST_MODEL="deepreinforce-ai/Ornith-1.0-35B"
ENV NATIVE_MODEL="moonshotai/Kimi-K2.7-Code"

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

CMD ["python", "app.py"]
