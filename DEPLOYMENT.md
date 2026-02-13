# 🚀 Deployment Guide for DUDU IV Hub

This guide provides a step-by-step process to deploy the DUDU IV Hub application.

## 1. Prerequisites
Ensure you have the following installed on your server or local machine:
- **Python 3.10+**
- **Git**
- **pip** (Python package manager)

## 2. Clone the Repository
Get the latest code from GitHub:
```bash
git clone https://github.com/SACHIN-6917/SNDA-DUDU.git
cd SNDA-DUDU
```
*If you already have the repo, just pull the latest changes:*
```bash
git pull origin main
```

## 3. Set Up Virtual Environment
Create an isolated environment for dependencies:
```bash
python -m venv venv
# Activate it:
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

## 4. Install Dependencies
Install all required Python packages:
```bash
pip install -r requirements.txt
```

## 5. Configure Environment Variables
Create a `.env` file in the `backend` directory (where `manage.py` is located) with the following keys:
```env
DEBUG=True
SECRET_KEY=your-secure-secret-key
ALLOWED_HOSTS=127.0.0.1,localhost,your-domain.com

# Email Settings (for Newsletter/Contact)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## 6. Database Setup
Apply migrations to set up the database:
```bash
cd backend
python manage.py migrate
```

## 7. Collect Static Files
Gather all CSS/JS/Images for production serving:
```bash
python manage.py collectstatic
```

## 8. Run the Server
### For Development:
```bash
python manage.py runserver
```
Access at: `http://127.0.0.1:8000`

### For Production (Linux/VPS):
Use **Gunicorn** and **Nginx**:
1. Install Gunicorn: `pip install gunicorn`
2. Run Gunicorn:
   ```bash
   gunicorn industrial_visit.wsgi:application --bind 0.0.0.0:8000
   ```
3. Configure Nginx to proxy requests to port 8000.

## 9. Verification
- Visit the website.
- Check the **"About"** link scrolls to Stats.
- Test **Newsletter Subscription** (footer).
- Test **Panda Bot** questions like "how to login".

✅ **Deployment Complete!**
