# Multi-stage build for React frontend

# Stage 1: Build
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the application
# Use REACT_APP_API_URL environment variable if provided, otherwise build with placeholder
ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=${REACT_APP_API_URL}

# Build and verify build output exists
RUN npm run build && \
    ls -la /app/build && \
    test -f /app/build/index.html || (echo "Build failed: index.html not found" && exit 1)

# Stage 2: Production server
FROM nginx:alpine

# Copy built assets from builder
COPY --from=builder /app/build /usr/share/nginx/html

# Remove default nginx config first
RUN rm -f /etc/nginx/conf.d/default.conf 2>/dev/null || true

# Copy our nginx configuration template
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

# Set proper permissions - make everything world-readable and executable for directories
RUN chmod -R 755 /usr/share/nginx/html && \
    chmod 644 /usr/share/nginx/html/index.html && \
    ls -la /usr/share/nginx/html && \
    test -f /usr/share/nginx/html/index.html && \
    echo "Files verified successfully"

# Expose port (Cloud Run will provide PORT env var)
EXPOSE 8080

# Set default PORT for nginx
ENV PORT=8080

# Install gettext package for envsubst
RUN apk add --no-cache gettext

# Create startup script to handle PORT variable and backend URL
RUN echo '#!/bin/sh' > /docker-entrypoint.sh && \
    echo 'set -e' >> /docker-entrypoint.sh && \
    echo 'PORT=${PORT:-8080}' >> /docker-entrypoint.sh && \
    echo 'BACKEND_API_URL=${BACKEND_API_URL:-http://localhost:8000/api}' >> /docker-entrypoint.sh && \
    echo 'export PORT' >> /docker-entrypoint.sh && \
    echo 'export BACKEND_API_URL' >> /docker-entrypoint.sh && \
    echo 'envsubst '"'"'$PORT $BACKEND_API_URL'"'"' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf' >> /docker-entrypoint.sh && \
    echo 'echo "Starting nginx on port $PORT with backend: $BACKEND_API_URL"' >> /docker-entrypoint.sh && \
    echo 'exec nginx -g "daemon off;"' >> /docker-entrypoint.sh && \
    chmod +x /docker-entrypoint.sh

# Start nginx with environment variable substitution
CMD ["/docker-entrypoint.sh"]

