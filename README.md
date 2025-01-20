<div align="center">

# 🦋 BioLog
[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![Django](https://img.shields.io/badge/Django-4.2+-green?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12+-blue?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-6+-red?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io)
[![Celery](https://img.shields.io/badge/Celery-5+-brightgreen?style=for-the-badge&logo=celery&logoColor=white)](https://docs.celeryq.dev)
[![Node.js](https://img.shields.io/badge/Node.js-14+-339933?style=for-the-badge&logo=node.js&logoColor=white)](https://nodejs.org)

An interactive web application for learning and testing knowledge about insects. The application features dynamic quizzes, user progression tracking, and social features.
</div>

## Features

### Quiz System
- Multiple choice and text input quiz modes
- Dynamic question loading with region and season-specific butterflies
- Real-time image loading from iNaturalist API
- Progress tracking during quiz sessions
- Detailed results analysis after completion

### User Features
- User profiles with statistics and achievements
- Social features (following other users)
- Achievement system with multiple badges:
- Profile customization with avatars
- User activity tracking and statistics

### Administrative Features
- Detailed statistics for administrators
- CSV export functionality for data analysis
- User management system
- Content moderation capabilities

### Technical Features
- Real-time notifications system
- Asynchronous question loading
- Responsive design for mobile and desktop
- Image optimization and caching
- CSRF protection
- Email verification system

## Technical Stack

### Backend
- Django
- Celery for asynchronous tasks
- PostgreSQL database
- Redis for caching

### Frontend
- HTML5/CSS3
- JavaScript
- Chart.js for data visualization
- Responsive design with media queries
- AJAX for dynamic content loading

### External Services
- iNaturalist API for butterfly images and data
- Email service for notifications

## Project Structure

```
quiz_app/
├── models/
│   ├── Species.py
│   ├── Quiz.py
│   └── User.py
├── views/
│   ├── quiz.py
│   ├── user.py
│   └── admin.py
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── templates/
│   ├── quiz/
│   ├── user/
│   └── admin/
├── tasks/
│   └── celery_tasks.py
└── utils/
    ├── image_utils.py
    └── quiz_utils.py
```

## Setup and Installation

1. Clone the repository:
```bash
git clone https://github.com/MBertoncini/BioLog.git
cd BioLog
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .myenv.example .env
```

5. Initialize the database:
```bash
python manage.py migrate
python manage.py loaddata initial_data.json
```

6. Start the development server:
```bash
python manage.py runserver
```

## Requirements

- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- Node.js 14+ (for building frontend assets)

## Configuration

The application requires several environment variables:

```env
DEBUG=True
SECRET_KEY=your_secret_key
DATABASE_URL=postgres://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0
INATURALIST_API_KEY=your_api_key
EMAIL_HOST=smtp.yourprovider.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email
EMAIL_HOST_PASSWORD=your_password
```

## Development

To set up the development environment:

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Set up pre-commit hooks:
```bash
pre-commit install
```

3. Run tests:
```bash
python manage.py test
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
