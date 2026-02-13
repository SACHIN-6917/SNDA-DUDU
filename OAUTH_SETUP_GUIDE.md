# Google OAuth Setup Guide

After setting up your Google OAuth credentials, you need to configure them in Django's database:

## Step 1: Get Google OAuth Credentials

1. Go to https://console.cloud.google.com/apis/credentials

2. Create a new project or select an existing one

3. Enable Google+ API

4. Create OAuth 2.0 Client ID (Web application)

5. Add authorized redirect URI:
   ```
   http://127.0.0.1:8000/accounts/google/login/callback/
   ```

6. Copy the Client ID and Client Secret

7. Update your `.env` file:
   ```
   GOOGLE_CLIENT_ID=your-actual-client-id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-actual-client-secret
   ```

## Step 2: Configure Google Social App in Django

### Method 1: Using Django Admin (Recommended)

1. Make sure your server is running:
   ```
   python manage.py runserver
   ```

2. Go to http://127.0.0.1:8000/admin/

3. Log in with your superuser account

4. Navigate to "Sites" and make sure you have a site with:
   - Domain name: 127.0.0.1:8000
   - Display name: DUDU IV Hub

5. Navigate to "Social applications" under "Social Accounts"

6. Click "Add Social Application" and create:

   **For Google:**
   - Provider: Google
   - Name: Google OAuth
   - Client id: [Your Google Client ID]
   - Secret key: [Your Google Client Secret]
   - Sites: Select your site (127.0.0.1:8000)

7. Save the application

### Method 2: Using Django Shell

If you prefer to set up via command line:

```python
python manage.py shell

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

# Get or create the site
site = Site.objects.get_or_create(
    id=1,
    defaults={
        'domain': '127.0.0.1:8000',
        'name': 'DUDU IV Hub'
    }
)[0]

# Create Google OAuth app
google_app = SocialApp.objects.create(
    provider='google',
    name='Google OAuth',
    client_id='YOUR_GOOGLE_CLIENT_ID',
    secret='YOUR_GOOGLE_CLIENT_SECRET',
)
google_app.sites.add(site)

print("Google OAuth configured successfully!")
```

## Step 3: Test the Integration

1. Restart your Django server
2. Go to the login page: http://127.0.0.1:8000/login/
3. Click "Continue with Google"
4. You should be redirected to Google's login page
5. After successful login, you'll be redirected back to your app

## Accessing the Settings Page

Once configured, users can manage their Google connection at:
- Direct URL: http://127.0.0.1:8000/settings/
- Via Navigation: Click on username dropdown → Settings

## Features Available:

1. **Change Email**: Manage email addresses
2. **Change Password**: Update account password
3. **Account Connections**: View connected social accounts
4. **Connect/Disconnect Google**: Link or unlink Google account
5. **Sign Out**: Log out from the account

## Troubleshooting

### "MultipleObjectsReturned" Error
If you encounter this error:
1. Go to Django Admin
2. Navigate to Social Applications
3. Delete duplicate Google apps
4. Keep only one Google app

### Google Login Doesn't Work
If social login doesn't work:
1. Verify your OAuth credentials in .env match exactly what's in Google Console
2. Check that redirect URI matches exactly (including http:// and port number)
3. Ensure the social app is added to the correct site in Django admin
4. Clear your browser cache and try again
5. Check Django server logs for error messages

### Redirect URI Mismatch
Make sure the redirect URI in Google Console exactly matches:
```
http://127.0.0.1:8000/accounts/google/login/callback/
```

Note: Don't use `localhost`, use `127.0.0.1` for consistency

## Production Deployment

When deploying to production:
1. Update the redirect URI in Google Console to your production domain
2. Update the Site domain in Django admin
3. Update ALLOWED_HOSTS in settings.py
4. Use environment variables for sensitive credentials
5. Enable HTTPS for security
