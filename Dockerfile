# Stage 1: Build the React frontend
FROM node:18-slim as builder

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
COPY tsconfig.json .
COPY vite.config.ts .
COPY tailwind.config.ts .
COPY postcss.config.js .
COPY client/ client/
RUN npm install --legacy-peer-deps

# Build the frontend
RUN npm run build

# Stage 2: Create the final Python application
FROM python:3.11-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code
COPY . .

# Copy the built frontend from the builder stage
COPY --from=builder /app/client/dist ./client/dist

# Expose the port the app runs on
EXPOSE 8080

# Creates a non-root user and changes ownership
RUN useradd -m -u 1000 appuser
USER appuser

# Run the application
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8080", "api.main:app"]