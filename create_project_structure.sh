#!/bin/bash

echo "🔧 Creating FastAPI Project Structure..."

# Core Application Files
touch requirements.txt .env config.py models.py main.py

# Services Layer
mkdir -p services
touch services/__init__.py \
      services/database_service.py \
      services/gemini_service.py \
      services/pdf_service.py

# Data Layer
mkdir -p data
touch data/__init__.py \
      data/seed_data.py

# Frontend
mkdir -p templates static
touch templates/index.html \
      static/styles.css \
      static/app.js

# Project Files
touch .gitignore README.md setup.py

# Deployment & Scripts
touch run.py quick_start.sh quick_start.bat Dockerfile docker-compose.yml

echo "✅ Project structure created successfully!"