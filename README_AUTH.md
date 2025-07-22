# Authentication and Branding Setup

This document explains how to set up authentication and customize branding for your organization.

## 🔐 Authentication System

### Basic Authentication
The system includes basic username/password authentication with the following features:

- **Default Credentials**: `admin` / `admin123`
- **Session Management**: 1-hour timeout
- **SQLite Database**: Stores user accounts in `auth.db`
- **Password Hashing**: Secure password storage using Werkzeug

### Azure AD Integration (Placeholder)
The system includes placeholders for Azure AD integration:

- **Azure AD Endpoints**: `/auth/azure` and `/auth/callback`
- **Configuration**: Set Azure AD credentials in environment variables
- **TODO**: Implement actual Azure AD authentication flow

## 🎨 Organization Branding

### Customizable Elements
You can customize the following branding elements:

1. **Organization Name**: `ORG_NAME`
2. **Logo**: `ORG_LOGO` (path to logo image)
3. **Background**: `ORG_BACKGROUND` (path to background image)
4. **Primary Color**: `ORG_PRIMARY_COLOR` (CSS color value)
5. **Secondary Color**: `ORG_SECONDARY_COLOR` (CSS color value)

### Branding Locations
- **Login Page**: Organization name, logo, and colors
- **Main Application**: Navigation bar, sidebar, and UI elements
- **CSS Variables**: Dynamic color application throughout the interface

## ⚙️ Configuration

### Environment Variables
Create a `.env` file or set environment variables:

```bash
# Authentication
ADMIN_USERNAME=your-admin-username
ADMIN_PASSWORD=your-secure-password
SECRET_KEY=your-secret-key

# Organization Branding
ORG_NAME=Your Company Name
ORG_LOGO=/static/images/your-logo.png
ORG_BACKGROUND=/static/images/your-background.jpg
ORG_PRIMARY_COLOR=#your-primary-color
ORG_SECONDARY_COLOR=#your-secondary-color

# Azure AD (when implementing)
AZURE_CLIENT_ID=your-azure-client-id
AZURE_CLIENT_SECRET=your-azure-client-secret
AZURE_TENANT_ID=your-azure-tenant-id
AZURE_REDIRECT_URI=http://your-domain/auth/callback
```

### File Structure
```
static/
├── images/
│   ├── logo.png          # Your organization logo
│   └── background.jpg    # Your background image
templates/
├── login.html           # Login page with branding
└── index_with_feedback.html  # Main app with branding
```

## 🚀 Setup Instructions

### 1. Basic Setup
```bash
# Install dependencies
pip install -r requirements_feedback.txt

# Set environment variables
export ADMIN_USERNAME=your-username
export ADMIN_PASSWORD=your-password
export ORG_NAME="Your Organization"

# Run the application
python app_with_feedback.py
```

### 2. Custom Branding
1. **Add Your Logo**: Place your logo in `static/images/logo.png`
2. **Add Background**: Place background image in `static/images/background.jpg`
3. **Set Colors**: Update `ORG_PRIMARY_COLOR` and `ORG_SECONDARY_COLOR`
4. **Update Name**: Set `ORG_NAME` to your organization name

### 3. Azure AD Integration (Future)
To implement Azure AD authentication:

1. **Register App**: Register your application in Azure AD
2. **Get Credentials**: Obtain Client ID, Client Secret, and Tenant ID
3. **Update Code**: Implement the Azure AD authentication flow in:
   - `app_with_feedback.py` (routes `/auth/azure` and `/auth/callback`)
   - `templates/login.html` (Azure AD login button)
4. **Set Environment Variables**: Configure Azure AD credentials

## 🔧 Customization Examples

### Example 1: Corporate Branding
```bash
export ORG_NAME="Acme Corporation"
export ORG_LOGO="/static/images/acme-logo.png"
export ORG_PRIMARY_COLOR="#1f4e79"
export ORG_SECONDARY_COLOR="#2e5984"
```

### Example 2: Law Firm Branding
```bash
export ORG_NAME="Smith & Associates Law"
export ORG_LOGO="/static/images/smith-law-logo.png"
export ORG_PRIMARY_COLOR="#8b4513"
export ORG_SECONDARY_COLOR="#a0522d"
```

### Example 3: Financial Institution
```bash
export ORG_NAME="Global Bank Ltd"
export ORG_LOGO="/static/images/global-bank-logo.png"
export ORG_PRIMARY_COLOR="#0066cc"
export ORG_SECONDARY_COLOR="#003366"
```

## 🔒 Security Considerations

### Production Deployment
1. **Change Default Credentials**: Update admin username/password
2. **Secure Secret Key**: Use a strong, random secret key
3. **HTTPS**: Always use HTTPS in production
4. **Session Security**: Configure secure session settings
5. **Azure AD**: Implement proper Azure AD authentication

### Security Best Practices
- Use strong passwords
- Implement rate limiting
- Add audit logging
- Regular security updates
- Monitor authentication attempts

## 📝 TODO Items

### Azure AD Implementation
- [ ] Implement Azure AD authentication flow
- [ ] Add token validation
- [ ] Handle user profile information
- [ ] Implement role-based access control

### Enhanced Security
- [ ] Add rate limiting for login attempts
- [ ] Implement password complexity requirements
- [ ] Add two-factor authentication
- [ ] Add session timeout warnings

### Branding Enhancements
- [ ] Add custom CSS themes
- [ ] Implement dark mode
- [ ] Add organization-specific fonts
- [ ] Create branded email templates

## 🆘 Troubleshooting

### Common Issues
1. **Login Not Working**: Check database initialization and credentials
2. **Branding Not Showing**: Verify image paths and environment variables
3. **Session Issues**: Check secret key configuration
4. **Azure AD Errors**: Verify Azure AD configuration

### Debug Commands
```bash
# Check database
sqlite3 auth.db "SELECT * FROM users;"

# Check environment variables
python -c "import os; print(os.environ.get('ORG_NAME', 'Not set'))"

# Test authentication
curl -X POST http://localhost:5001/login -d "username=admin&password=admin123"
```

## 📞 Support

For issues with authentication or branding:
1. Check the logs in the terminal
2. Verify environment variable configuration
3. Ensure database files are created properly
4. Test with default credentials first 