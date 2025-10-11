#!/bin/bash
# Build script for Render deployment

echo "🚀 Starting build process..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Navigate to React app directory and build
echo "⚛️  Building React dashboard..."
cd wtestapp/templates/wtestapp/admin_minidash
npm install
npm run build

# Go back to root
cd ../../../../

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Build completed successfully!"
