# DevPulse

A Django REST API backend for tracking developer activities and GitHub integration, powered by Firebase Authentication.

## Overview

DevPulse helps developers track their daily coding activities and maintain development streaks. It integrates with GitHub to automatically sync contributions and provides insights into your development patterns.

## Features

- **Firebase Authentication**: Secure user authentication using Firebase Auth
- **Activity Tracking**: Log daily coding, learning, and debugging activities
- **Streak Calculation**: Track current and longest development streaks
- **GitHub Integration**: 
  - Sync activities from GitHub events
  - Fetch comprehensive GitHub statistics
  - Auto-categorize GitHub events into activity types
- **RESTful API**: Clean, well-structured API endpoints

## Tech Stack

- **Framework**: Django 6.0.1
- **API**: Django REST Framework 3.16.1
- **Authentication**: Firebase Admin SDK 7.1.0
- **Database**: SQLite (development)
- **Python**: 3.14+

## Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd devpulse
```

2. **Install dependencies**
```bash
uv pip install -r requirements.txt
# or
pip install -r requirements.txt
```

3. **Set up Firebase**
   - Create a Firebase project at [Firebase Console](https://console.firebase.google.com)
   - Download your service account key
   - Save it as `firebase-service-account.json` in the project root
   - Create a `.env` file and add your Firebase API key:
```
   FIREBASE_API_KEY=your_firebase_web_api_key
```

4. **Run migrations**
```bash
python manage.py migrate
```

5. **Start the development server**
```bash
python manage.py runserver
```

## API Endpoints

### Authentication

- **POST** `/api/auth/signup/` - Create a new user
- **POST** `/api/auth/login/` - Login and get ID token
- **GET** `/test-auth/` - Test authentication (requires auth)

### Activities

- **POST** `/api/activities/` - Create a new activity
- **GET** `/api/activities/` - List all user activities

### Streaks

- **GET** `/api/streak/` - Get current and longest streak

### GitHub Integration

- **POST** `/api/github/sync/` - Sync activities from GitHub
- **GET** `/api/github/stats/` - Get GitHub profile statistics

## Models

### Activity
Tracks daily developer activities with types:
- `coding` - Writing code, commits, PRs
- `learning` - Watching repos, forking projects
- `debugging` - Issues, comments

### GitHubProfile
Stores GitHub integration settings:
- GitHub username
- Optional access token (for private repos)
- Last sync timestamp
- Auto-sync preference

## Authentication

All protected endpoints require a Firebase ID token in the Authorization header:
```
Authorization: Bearer <firebase_id_token>
```

## Testing

Use the included PowerShell test script to verify all endpoints:
```powershell
.\test-devpulse.ps1
```

Or with custom parameters:
```powershell
.\test-devpulse.ps1 -Email "your@email.com" -Password "yourpassword"
```

## Project Structure
```
devpulse/
├── activities/          # Main app
│   ├── models.py       # Activity and GitHubProfile models
│   ├── views.py        # API endpoints
│   ├── serializers.py  # DRF serializers
│   └── authentication.py # Firebase auth backend
├── devpulse/           # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── firebase.py     # Firebase initialization
└── manage.py
```

## Configuration

### Settings
- `DEBUG`: Set to `False` in production
- `SECRET_KEY`: Generate a new key for production
- `ALLOWED_HOSTS`: Configure for your domain

### Database
Currently using SQLite. For production, configure PostgreSQL or MySQL in `settings.py`.

## GitHub Event Mapping

GitHub events are automatically mapped to activity types:

| GitHub Event | Activity Type |
|--------------|--------------|
| PushEvent, PullRequestEvent, CreateEvent | coding |
| IssuesEvent, IssueCommentEvent | debugging |
| WatchEvent, ForkEvent | learning |

## Development

### Running Tests
```bash
python manage.py test
```

### Creating Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

## Security Notes

⚠️ **Important**: 
- Never commit `firebase-service-account.json` to version control
- Store sensitive credentials in environment variables
- Use Django's `SECRET_KEY` generator for production
- Enable HTTPS in production
- Consider encrypting GitHub tokens before storing

## License

[Your License Here]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on GitHub.