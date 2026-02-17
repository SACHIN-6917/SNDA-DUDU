# Railway Deployment Guide

This guide will help you deploy your SNDA-DUDU Django application to Railway, getting all features (chatbot, authentication, payments) working exactly like localhost.

## Prerequisites

- GitHub account with your code at https://github.com/SACHIN-6917/SNDA-DUDU
- Railway account (sign up at https://railway.app with GitHub)
- Google OAuth credentials
- OpenAI API key

## Step 1: Create Railway Project

1. Visit https://railway.app and sign in with GitHub
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose **SACHIN-6917/SNDA-DUDU** repository
5. Railway will automatically detect Django application

## Step 2: Add PostgreSQL Database

1. In your Railway project dashboard, click **"+ New"**
2. Select **"Database"** → **"Add PostgreSQL"**
3. Railway automatically creates `DATABASE_URL` environment variable
4. Your Django app will automatically use PostgreSQL in production

## Step 3: Configure Environment Variables

Click on your web service, go to **"Variables"** tab, and add:

### Required Variables

```env
SECRET_KEY=<generate-a-new-secret-key-for-production>
DEBUG=False
RAILWAY_PUBLIC_DOMAIN=${{RAILWAY_PUBLIC_DOMAIN}}
OPENAI_API_KEY=<your-openai-api-key>
```

### Optional (for Google OAuth)

```env
GOOGLE_CLIENT_ID=<your-google-client-id>
GOOGLE_CLIENT_SECRET=<your-google-client-secret>
```

### Generate SECRET_KEY

Run this command locally to generate a secure key:

```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Step 4: Deploy

1. Railway automatically deploys when you push to GitHub
2. Wait for build to complete (2-5 minutes)
3. Click on the generated URL (e.g., `https://snda-dudu-production.up.railway.app`)

## Step 5: Run Database Migrations

1. In Railway dashboard, click on your web service
2. Go to **"Settings"** → **"Deploy"**
3. Under **"Custom Start Command"**, it should be:
   ```
   cd backend && gunicorn industrial_visit.wsgi:application --bind 0.0.0.0:$PORT
   ```
4. To run migrations, use Railway CLI or one-time command:
   ```bash
   cd backend && python manage.py migrate
   ```

### Using Railway CLI (Recommended)

Install Railway CLI:
```bash
npm install -g @railway/cli
```

Login and run migrations:
```bash
railway login
railway link
railway run python backend/manage.py migrate
railway run python backend/manage.py createsuperuser
```

## Step 6: Create Admin User

Using Railway CLI:
```bash
railway run python backend/manage.py createsuperuser
```

Or use your existing admin script:
```bash
railway run python backend/scripts/create_admin.py
```

## Step 7: Collect Static Files

Railway automatically runs this during deployment from `railway.json`:
```bash
python manage.py collectstatic --noinput
```

If it didn't run, manually execute:
```bash
railway run python backend/manage.py collectstatic --noinput
```

## Step 8: Update Google OAuth Redirect URIs

1. Go to https://console.cloud.google.com/apis/credentials
2. Edit your OAuth 2.0 Client ID
3. Under **"Authorized redirect URIs"**, add:
   ```
   https://your-app.railway.app/accounts/google/login/callback/
   ```
4. Replace `your-app.railway.app` with your actual Railway domain

## Step 9: Load Initial Data (Optional)

If you want to seed the production database with industrials and feedback:

```bash
railway run python backend/seed_industrials.py
railway run python backend/seed_feedbacks.py
```

## Step 10: Test Your Application

Visit your Railway URL and test:

- ✅ Homepage loads with correct styling
- ✅ Industrial visits display
- ✅ Login/Registration works
- ✅ Google OAuth works (after updating redirect URIs)
- ✅ Chatbot responds (Panda Bot)
- ✅ Feedback submission works
- ✅ Payment page loads
- ✅ Admin dashboard at `/admin` works

## Troubleshooting

### Static Files Not Loading

Check that `STATICFILES_STORAGE` is set:
```python
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### Database Connection Errors

Verify `DATABASE_URL` is set in Railway environment variables (automatically set when you add PostgreSQL).

### 403 CSRF Errors

Make sure `RAILWAY_PUBLIC_DOMAIN` is set in environment variables and `settings.py` includes it in `CSRF_TRUSTED_ORIGINS`.

### Chatbot Not Working

Verify `OPENAI_API_KEY` is set in Railway environment variables.

## Continuous Deployment

Railway automatically deploys when you push to GitHub:

```bash
git add .
git commit -m "your changes"
git push origin main
```

Railway will:
1. Pull latest code
2. Install dependencies from `requirements.txt`
3. Collect static files
4. Restart the application

## Monitoring

- **Logs**: View in Railway dashboard under "Deployments" → "View Logs"
- **Metrics**: CPU, Memory, Network usage in Railway dashboard
- **Alerts**: Configure in Railway settings

## Cost

- **Free Tier**: $5 credit/month
- **Estimated Usage**: $3-5/month for small app
- **Upgrade**: $5/month for more resources if needed

## Custom Domain (Optional)

1. In Railway dashboard, go to **"Settings"** → **"Domains"**
2. Click **"Custom Domain"**
3. Add your domain (e.g., `dudu.yourdomain.com`)
4. Update DNS records as instructed
5. Update `ALLOWED_HOSTS` in environment variables

## Security Checklist

- ✅ `DEBUG=False` in production
- ✅ Strong `SECRET_KEY` generated
- ✅ `SECURE_SSL_REDIRECT=True` (handled automatically)
- ✅ `.env` file not committed to GitHub
- ✅ All API keys in environment variables
- ✅ CSRF protection enabled
- ✅ Secure cookies in production

## Support

If you encounter issues:
1. Check Railway logs
2. Review Django deployment checklist: `python manage.py check --deploy`
3. Verify all environment variables are set
4. Check Railway community: https://help.railway.app

---

**Your application is now live! 🎉**

Visit your Railway URL to see your fully functional Django application with all features working just like localhost.
