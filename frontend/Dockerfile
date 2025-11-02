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

# nginx:alpine automatically processes templates in /etc/nginx/templates/ 
# and substitutes environment variables

