# SNDA-DUDU - Industrial Visit Management System

A comprehensive Django-based web application for managing industrial visits, student registrations, feedback, and payments. Features include user authentication (including Google OAuth), an AI-powered chatbot, and a modern responsive interface.

## ✨ Features

- 🔐 **Authentication System**: Email/password login, Google OAuth, and passkey support
- 🏭 **Industrial Visit Management**: Browse and enquire about industrial visits
- 💬 **AI Chatbot**: Panda Bot powered by OpenAI to assist users with queries
- 💰 **Payment Integration**: Payment processing interface
- 📝 **Feedback System**: Collect and manage user feedback
- 📊 **Admin Dashboard**: Manage industrials, users, and site content
- 🎨 **Modern UI**: Responsive design with light/dark theme support
- 👤 **User Profiles**: Account management and settings

## 🛠️ Technologies Used

- **Backend**: Django 5.1.5, Python 3.x
- **Database**: MySQL
- **Authentication**: Django Allauth (Google OAuth)
- **Frontend**: HTML5, CSS3, JavaScript
- **AI Integration**: OpenAI API
- **Version Control**: Git

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- MySQL Server
- Git
- pip (Python package manager)

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/SACHIN-6917/SNDA-DUDU.git
cd SNDA-DUDU
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the `backend` directory by copying the example:

```bash
copy .env.example .env  # Windows
# or
cp .env.example .env    # macOS/Linux
```

Edit the `.env` file with your configuration:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database
DB_NAME=industrial_visit
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306

# Google OAuth (Optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# OpenAI Chatbot
OPENAI_API_KEY=your-openai-api-key
```

**See [OAUTH_SETUP_GUIDE.md](OAUTH_SETUP_GUIDE.md) for Google OAuth configuration.**

### 5. Setup Database

Create the MySQL database:

```sql
CREATE DATABASE industrial_visit;
```

Run migrations:

```bash
python manage.py migrate
```

### 6. Create Admin User

```bash
python manage.py createsuperuser
# Or use the script:
python scripts/create_admin.py
```

### 7. Load Initial Data (Optional)

```bash
python seed_industrials.py
python seed_feedbacks.py
```

### 8. Run Development Server

```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000 to see the application.

## 📁 Project Structure

```
SNDA-DUDU/
├── backend/                  # Django backend
│   ├── industrial_visit/     # Main project settings
│   ├── dudu/                 # Main application
│   ├── templates/            # HTML templates
│   ├── static/               # Static files (CSS, JS, images)
│   ├── scripts/              # Utility scripts
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example
│   └── .env                  # Your local config (not in git)
├── static/                   # Frontend static files
├── docs/                     # Documentation
├── DEPLOYMENT.md             # Deployment guide
├── OAUTH_SETUP_GUIDE.md      # OAuth configuration guide
└── README.md                 # This file
```

## 🔧 Configuration

### Google OAuth Setup
See [OAUTH_SETUP_GUIDE.md](OAUTH_SETUP_GUIDE.md) for detailed instructions.

### Chatbot Configuration
The chatbot uses OpenAI's API. Set `OPENAI_API_KEY` in your `.env` file. If you want to use a fallback mode without API calls, set `CHATBOT_FALLBACK_MODE=True`.

## 🎯 Usage

### For Users
1. **Browse Industrials**: View available industrial visits on the home page
2. **Enquire**: Fill out the enquiry form for industrial visits
3. **Login**: Create an account or login with Google
4. **Chat**: Use the Panda Bot (chatbot icon) for assistance
5. **Feedback**: Submit feedback about your experience
6. **Payment**: Process payments for industrial visits

### For Administrators
1. Access admin panel at http://127.0.0.1:8000/admin
2. Manage industrial visits, users, feedback, and enquiries
3. View statistics and monitor system activity

## 🚀 Deployment

For production deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

## 📝 Available Scripts

- `python manage.py runserver` - Start development server
- `python manage.py migrate` - Apply database migrations
- `python manage.py createsuperuser` - Create admin user
- `python scripts/create_admin.py` - Create admin with predefined credentials
- `python seed_industrials.py` - Load sample industrial data
- `python seed_feedbacks.py` - Load sample feedback data
- `python list_industrials.py` - List all industrials in database

## 🔒 Security Notes

- Never commit the `.env` file to version control
- Change the `SECRET_KEY` in production
- Set `DEBUG=False` in production
- Use strong database passwords
- Keep API keys secure
- Configure ALLOWED_HOSTS for production

## 🤝 Contributing

This is a private project. For any issues or suggestions, please contact the repository owner.

## 📄 License

This project is proprietary. All rights reserved.

## 👤 Author

**SACHIN**
- GitHub: [@SACHIN-6917](https://github.com/SACHIN-6917)

## 📞 Support

For issues or questions:
1. Check the documentation in the `docs/` folder
2. Review [DEPLOYMENT.md](DEPLOYMENT.md) for deployment issues
3. Contact the repository owner

---

**Built with ❤️ using Django**
