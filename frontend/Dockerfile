# ============================================================
# SecureWatch Frontend — Multi-stage Dockerfile
# Stage 1: Build React app with Node.js
# Stage 2: Serve with Nginx
# ============================================================

# ─── Stage 1: Build ─────────────────────────────────────────
FROM node:20-alpine AS builder

LABEL maintainer="SecureWatch Team"
LABEL description="React frontend build stage"

# Set working directory
WORKDIR /app

# Install dependencies first (better layer caching)
COPY package.json package-lock.json* ./

# Use npm ci for reproducible builds
RUN npm ci --frozen-lockfile --prefer-offline

# Copy source code
COPY . .

# Build production bundle
ARG VITE_API_BASE_URL=http://localhost:8000
ARG VITE_WS_BASE_URL=ws://localhost:8000
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_WS_BASE_URL=$VITE_WS_BASE_URL

RUN npm run build

# ─── Stage 2: Serve ─────────────────────────────────────────
FROM nginx:1.25-alpine AS production

LABEL maintainer="SecureWatch Team"
LABEL description="SecureWatch React frontend served via Nginx"

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built files from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Set correct permissions
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html

# Create nginx cache directories
RUN mkdir -p /var/cache/nginx/client_temp && \
    chown -R nginx:nginx /var/cache/nginx

EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -qO- http://localhost:80/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
