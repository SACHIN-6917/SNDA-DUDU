# OAuth Setup Guide for DUDU Industrial Visit Management System

## 🔐 Quick OAuth Configuration Guide

This guide will help you set up Google and Facebook OAuth login for your application.

---

## 🟢 Google OAuth Setup

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Name your project: "DUDU IV Hub"
4. Click "Create"

### Step 2: Enable Google+ API

1. In the left menu, go to "APIs & Services" → "Library"
2. Search for "Google+ API"
3. Click "Enable"

### Step 3: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Configure OAuth consent screen (if prompted):
   - User Type: External
   - App name: DUDU IV Hub
   - User support email: your-email@gmail.com
   - Developer contact: your-email@gmail.com
   - Save and Continue through all steps

4. Create OAuth Client ID:
   - Application type: **Web application**
   - Name: DUDU IV Hub Web Client
   - Authorized JavaScript origins:
     ```
     http://localhost:8000
     http://127.0.0.1:8000
     ```
   - Authorized redirect URIs:
     ```
     http://localhost:8000/accounts/google/login/callback/
     http://127.0.0.1:8000/accounts/google/login/callback/
     ```
   - Click "Create"

5. **Copy the credentials:**
   - Client ID: `your-client-id.apps.googleusercontent.com`
   - Client Secret: `your-client-secret`

### Step 4: Update .env File

```bash
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
```

### Step 5: Add to Django Admin (Alternative Method)

If using Django Allauth's database configuration:

1. Start your Django server: `python manage.py runserver`
2. Go to: http://127.0.0.1:8000/admin/
3. Login with superuser credentials
4. Go to "Sites" → Click on "example.com"
5. Change domain to: `127.0.0.1:8000` or `localhost:8000`
6. Save
7. Go to "Social applications" → "Add social application"
   - Provider: Google
   - Name: Google OAuth
   - Client ID: [paste your client ID]
   - Secret key: [paste your secret]
   - Sites: Select your site
   - Save

---

## 🔵 Facebook OAuth Setup

### Step 1: Create Facebook App

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Click "My Apps" → "Create App"
3. Choose "Consumer" as app type
4. App Display Name: DUDU IV Hub
5. App Contact Email: your-email@gmail.com
6. Click "Create App"

### Step 2: Add Facebook Login Product

1. In your app dashboard, click "Add Product"
2. Find "Facebook Login" and click "Set Up"
3. Choose "Web" platform
4. Site URL: `http://localhost:8000`
5. Click "Save" and "Continue"

### Step 3: Configure OAuth Redirect URIs

1. In left menu, go to "Facebook Login" → "Settings"
2. Add to "Valid OAuth Redirect URIs":
   ```
   http://localhost:8000/accounts/facebook/login/callback/
   http://127.0.0.1:8000/accounts/facebook/login/callback/
   ```
3. Save Changes

### Step 4: Get App Credentials

1. Go to "Settings" → "Basic"
2. **Copy the credentials:**
   - App ID: `your-app-id`
   - App Secret: `your-app-secret` (click "Show" to reveal)

### Step 5: Update .env File

```bash
FACEBOOK_APP_ID=your-app-id
FACEBOOK_APP_SECRET=your-app-secret
```

### Step 6: Make App Live (for production)

For testing, keep app mode as "Development"
For production:
1. Complete App Review process
2. Toggle app to "Live" mode

---

## 🔑 Passkey (WebAuthn) Setup

### Overview
Passkeys use WebAuthn for passwordless authentication using biometrics or security keys.

### Implementation Status
- **Current**: Placeholder button exists in login.html
- **Required**: WebAuthn API integration

### Quick Implementation (Optional)

1. Install package:
```bash
pip install django-allauth-passkey
```

2. Add to INSTALLED_APPS in settings.py:
```python
INSTALLED_APPS = [
    ...
    'allauth.mfa',  # Required for passkey
]
```

3. Run migrations:
```bash
python manage.py migrate
```

4. The passkey button in login.html will automatically work with django-allauth

---

## 🧪 Testing OAuth Login

### Test Google Login:
1. Navigate to: http://127.0.0.1:8000/login/
2. Click "Continue with Google"
3. Select your Google account
4. Authorize the app
5. You should be redirected back and logged in

### Test Facebook Login:
1. Navigate to: http://127.0.0.1:8000/login/
2. Click "Continue with Facebook"
3. Login to Facebook
4. Authorize the app
5. You should be redirected back and logged in

---

## 🔧 Troubleshooting

### Google OAuth Issues

**Error: "redirect_uri_mismatch"**
- Solution: Ensure callback URL in Google Console exactly matches Django URL
- Check: `http://127.0.0.1:8000/accounts/google/login/callback/`

**Error: "access_denied"**
- Solution: Ensure user authorized all required scopes
- Check OAuth consent screen configuration

### Facebook OAuth Issues

**Error: "URL Blocked"**
- Solution: Add URL to Valid OAuth Redirect URIs in Facebook app settings

**Error: "App Not Set Up"**
- Solution: Ensure Facebook Login product is added and configured

### Common Django Issues

**Error: "Social account not found"**
- Solution: Run migrations: `python manage.py migrate`
- Ensure django-allauth is in INSTALLED_APPS

**Error: "Site matching query does not exist"**
- Solution: Update Site in Django admin to match your domain
- Set SITE_ID = 1 in settings.py

---

## 📋 Complete .env Template

```bash
# Django Settings
SECRET_KEY=django-insecure-=-*ov$fr-k)phd#91hsu^yk&eg35c!-gw$d#1$q7tt1y756y9i
DEBUG=True

# Database Configuration
DB_NAME=industrial_visit
DB_USER=root
DB_PASSWORD=sachin6917
DB_HOST=localhost
DB_PORT=3306

# OAuth - Google
GOOGLE_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abcdefghijklmnopqrstuvwxyz

# OAuth - Facebook
FACEBOOK_APP_ID=1234567890123456
FACEBOOK_APP_SECRET=abcdef1234567890abcdef1234567890

# Chatbot Configuration
OPENAI_API_KEY=sk-proj-your-openai-api-key-here
CHATBOT_FALLBACK_MODE=True

# Payment Gateway - Razorpay
RAZORPAY_KEY_ID=rzp_test_1234567890abcd
RAZORPAY_KEY_SECRET=abcdefghijklmnopqrstuvwxyz123456
RAZORPAY_ENABLED=True

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password

# Site Configuration
SITE_URL=http://127.0.0.1:8000
ALLOWED_HOSTS=127.0.0.1,localhost
```

---

## ✅ Verification Checklist

- [ ] Google Cloud project created
- [ ] Google OAuth Client ID and Secret obtained
- [ ] Facebook App created
- [ ] Facebook App ID and Secret obtained
- [ ] .env file updated with credentials
- [ ] Django server restarted
- [ ] Site domain configured in Django admin
- [ ] Social applications added in Django admin (if using DB config)
- [ ] Google login tested successfully
- [ ] Facebook login tested successfully

---

## 🚀 Next Steps After OAuth Setup

1. **Test all authentication methods**
2. **Implement login success animation** (already in code)
3. **Set up Razorpay payment gateway**
4. **Complete account profile functionality**
5. **Deploy to production** (remember to update redirect URLs)

---

## 📞 Support

If you encounter issues:
1. Check Django logs: Look at terminal where `python manage.py runserver` is running
2. Check browser console: Press F12 → Console tab
3. Verify .env variables are loaded: Add `print(settings.GOOGLE_CLIENT_ID)` in views.py

Need help? Contact the development team or check:
- Django Allauth Docs: https://django-allauth.readthedocs.io/
- Google OAuth Docs: https://developers.google.com/identity/protocols/oauth2
- Facebook Login Docs: https://developers.facebook.com/docs/facebook-login/
