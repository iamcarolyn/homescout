FROM python:3.11-slim

# Install Node.js 20
RUN apt-get update && apt-get install -y \
    curl \
    supervisor \
    nginx \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python backend
COPY agents/ ./agents/
COPY tasks/ ./tasks/
COPY tools/ ./tools/
COPY config.py crew.py server.py scout.py ./

# Install and build Next.js frontend
COPY frontend/package*.json ./frontend/
RUN cd frontend && npm ci --no-audit --no-fund

COPY frontend/ ./frontend/
RUN cd frontend && npm run build && \
    cp -r .next/static .next/standalone/.next/ && \
    cp -r public .next/standalone/

# Create output directory
RUN mkdir -p /app/output

# Nginx and supervisor config
COPY nginx.conf /etc/nginx/nginx.conf
COPY supervisord.conf /etc/supervisor/conf.d/homescout.conf

EXPOSE 8080

CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
