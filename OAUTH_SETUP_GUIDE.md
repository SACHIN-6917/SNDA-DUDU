# Django Allauth Social App Setup Guide

After setting up your Google and Facebook OAuth credentials, you need to configure them in Django's database:

## Method 1: Using Django Admin (Recommended)

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

   **For Facebook:**
   - Provider: Facebook
   - Name: Facebook OAuth
   - Client id: [Your Facebook App ID]
   - Secret key: [Your Facebook App Secret]
   - Sites: Select your site (127.0.0.1:8000)

7. Save both applications

## Method 2: Using Django Shell

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

# Create Facebook OAuth app
facebook_app = SocialApp.objects.create(
    provider='facebook',
    name='Facebook OAuth',
    client_id='YOUR_FACEBOOK_APP_ID',
    secret='YOUR_FACEBOOK_APP_SECRET',
)
facebook_app.sites.add(site)

print("Social apps configured successfully!")
```

## Accessing the Settings Page

Once configured, users can access the settings page at:
- Direct URL: http://127.0.0.1:8000/settings/
- Via Navigation: Click on username dropdown → Settings

## Features Available:

1. **Change Email**: Manage email addresses
2. **Change Password**: Update account password
3. **Account Connections**: View all connected social accounts
4. **Connect/Disconnect Google**: Link or unlink Google account
5. **Connect/Disconnect Facebook**: Link or unlink Facebook account
6. **Sign Out**: Log out from the account

## Troubleshooting

If you encounter "MultipleObjectsReturned" error:
1. Go to Django Admin
2. Navigate to Social Applications
3. Delete duplicate Google or Facebook apps
4. Keep only one of each

If social login doesn't work:
1. Verify your OAuth credentials in .env
2. Check that redirect URIs match exactly
3. Ensure the social app is added to the correct site in Django admin
