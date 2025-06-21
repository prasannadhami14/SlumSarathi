# SlumSarathi

**SlumSarathi** is a comprehensive web platform built with Django, designed to empower and connect communities by providing easy access to essential services, educational resources, and local events.

## ✨ Key Features

-   **User Authentication**: Secure user registration, login, and profile management.
-   **Service Listings**: Users can browse and request essential services. Service providers can manage incoming requests.
-   **Resource Sharing**: A repository for uploading and accessing important documents and educational materials.
-   **Event Management**: Users can create, publish, and manage events. The platform notifies all users when a new event is published.
-   **Event Registration**: Simple, one-click event registration with email confirmations.
-   **Dynamic Search**: Real-time, AJAX-powered search across Services, Resources, and Events.
-   **Responsive UI**: A clean, modern, and mobile-friendly interface built with Bootstrap 5.
-   **Email Notifications**: Automated, professionally styled emails for key actions like event registration and publication.

## 🛠️ Technology Stack

-   **Backend**: Django
-   **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
--   **Database**: MySQL (configured with `mysqlclient`)
-   **Widgets**: `django-widget-tweaks` for form styling.
-   **Environment Management**: `django-environ`

## 📁 Folder Structure

Here is a high-level overview of the project's structure:

```
slumSarathi/
├── apps/
│   ├── accounts/       # Manages user authentication, profiles
│   ├── events/         # Manages event creation, listing, registration
│   ├── resources/      # Manages resource uploads and listings
│   └── services/       # Manages service listings and requests
├── media/              # Stores user-uploaded files (e.g., event images, resources)
├── static/             # Contains global static files (CSS, JS, images)
├── templates/          # Contains base HTML templates and layouts
│   ├── accounts/
│   ├── events/
│   ├── resources/
│   ├── services/
│   └── base.html       # Main site template
├── slumSarathi/        # Main Django project configuration
│   ├── settings.py     # Project settings
│   └── urls.py         # Root URL configuration
├── .env.example        # Example environment variables
├── manage.py           # Django's command-line utility
└── requirements.txt    # Python dependencies
```

## 🚀 Setup and Installation

Follow these steps to get the project running locally.

### 1. Prerequisites

-   Python 3.8+
-   A running MySQL database server.

### 2. Clone the Repository

```bash
git clone https://github.com/yourusername/slumSarathi.git
cd slumSarathi
```

### 3. Set Up a Virtual Environment

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a file named `.env` in the project root by copying the example file:

```bash
cp .env.example .env
```

Now, open the `.env` file and fill in the required values:

```ini
# .env

# SECURITY WARNING: a strong, unique secret key is required
SECRET_KEY='your-strong-secret-key'

# Set to True for development, False for production
DEBUG=True

# Database Configuration
DB_NAME='slumsarathi_db'
DB_USER='your_db_user'
DB_PASSWORD='your_db_password'
DB_HOST='localhost'
DB_PORT='3306'

# Email Configuration (Example using Gmail)
EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL='your-email@gmail.com'
EMAIL_HOST='smtp.gmail.com'
EMAIL_PORT=587
EMAIL_HOST_USER='your-email@gmail.com'
EMAIL_HOST_PASSWORD='your-gmail-app-password'
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
```

### 6. Apply Database Migrations

This will set up the database schema.

```bash
python manage.py migrate
```

### 7. Create a Superuser

This allows you to access the Django admin panel.

```bash
python manage.py createsuperuser
```

### 8. Run the Development Server

You're all set! Start the server with:

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`.

## 🤝 Contributing

Contributions are welcome! Please feel free to fork the repository, make changes, and submit a pull request.

1.  Fork the repository.
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.
