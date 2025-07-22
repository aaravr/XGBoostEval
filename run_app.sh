#!/bin/bash

# Set environment variables for authentication and branding
export ADMIN_USERNAME=admin
export ADMIN_PASSWORD=admin123
export SECRET_KEY=your-secret-key-change-in-production
export ORG_NAME="Legal Name Comparison System"
export ORG_LOGO="/static/images/logo.png"
export ORG_BACKGROUND="/static/images/background.jpg"
export ORG_PRIMARY_COLOR="#007bff"
export ORG_SECONDARY_COLOR="#6c757d"

# Azure AD placeholders (for future implementation)
export AZURE_CLIENT_ID=your-azure-client-id
export AZURE_CLIENT_SECRET=your-azure-client-secret
export AZURE_TENANT_ID=your-azure-tenant-id
export AZURE_REDIRECT_URI=http://localhost:5001/auth/callback

# Session configuration
export SESSION_TIMEOUT=3600

echo "🚀 Starting Legal Name Comparison System with Authentication"
echo "📝 Organization: $ORG_NAME"
echo "🎨 Primary Color: $ORG_PRIMARY_COLOR"
echo "🔐 Default Login: admin / admin123"
echo "🌐 Access URL: http://localhost:5001"
echo ""

# Run the application
python app_with_feedback.py 