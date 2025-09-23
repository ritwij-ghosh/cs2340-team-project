# HireBuzz

A Django-based web application for connecting early-career job seekers with recruiters. HireBuzz serves as a comprehensive job board platform with features for professional profiles, job postings, applications, and communication between users.

## Features

- **Professional Profiles** - Job seekers can create and manage professional profiles
- **Job Postings** - Recruiters can post job opportunities
- **Application Management** - Streamlined job application process
- **User Communication** - Messaging system between job seekers and recruiters
- **User Authentication** - Secure account management system

## Technology Stack

- **Backend**: Django 5.0
- **Database**: SQLite
- **Frontend**: Bootstrap 5.3.3 with custom CSS
- **Icons**: FontAwesome

## Project Structure

```
hirebuzz/
├── hirebuzz/           # Main Django project directory
│   ├── templates/      # Base templates
│   └── static/         # Static files (CSS, JS, images)
├── home/              # Landing page and navigation
├── accounts/          # User authentication
├── profiles/          # Professional profiles
├── jobs/             # Job posting and browsing
├── applications/     # Job application management
├── communications/   # User messaging system
└── db.sqlite3        # SQLite database
```

## Getting Started

### Prerequisites

- Python 3.x
- Django 5.0

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd cs2340-team-project
   ```

2. Apply database migrations:
   ```bash
   python manage.py migrate
   ```

3. Create a superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```

4. Start the development server:
   ```bash
   python manage.py runserver
   ```

5. Visit `http://127.0.0.1:8000/` in your browser

## Development Commands

### Database Operations
```bash
# Create migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### Development Tools
```bash
# Start development server
python manage.py runserver

# Access Django shell for debugging
python manage.py shell
```

## Current Status

This project is in active development. The basic Django structure is in place with all apps scaffolded, but implementation of models, views, and URL patterns is ongoing.

## Contributing

This is a CS 2340 team project. Please follow the established code structure and Django best practices when contributing.