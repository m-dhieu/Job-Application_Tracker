# Job Application Tracker

## Table of Contents

* [Overview](#overview)
* [Features](#features)
* [Live URL](#live-url)
* [Demo Video](#demo-video)
* [Repository Structure](#repository-structure)
* [Technology Stack](#technology-stack)
* [Database Schema](#database-schema)
* [API Server & Frontend](#api-server--frontend)
* [Docker & Deployment](#docker--deployment)
* [Testing](#testing)
* [Environment](#environment)
* [Setup Instructions](#setup-instructions)
* [Development Workflow](#development-workflow)
* [Troubleshooting](#troubleshooting)
* [Team](#team)
* [Contributing](#contributing)
* [License](#license)
* [Contact](#contact)

---

## Overview

The **Job Application Tracker** is a comprehensive platform to manage, track, and analyze job applications. It integrates a robust backend API built with FastAPI, a modern frontend interface, and a relational SQLite database. Users can register, apply to jobs, track application statuses, and view detailed analytics about their job search progress.

---

## Features

*  **User Registration & Authentication** - Secure user management with password hashing and JWT tokens
*  **Application Management** - Create, update, and track job applications
*  **Status Tracking** - Detailed status history and audit trails for each application
*  **Analytics & Statistics** - Success rates, response rates, and application trends
*  **RESTful API** - Complete API documentation with Swagger UI
*  **Docker Containerization** - Backend and frontend containerized deployments
*  **CI/CD Automation** - GitHub Actions for automated builds and Docker Hub deployment
*  **Interactive Frontend** - Modern web interface for managing applications
*  **Comprehensive Testing** - 123+ unit, integration, and E2E tests (100% passing)
*  **Data Integrity** - Referential integrity constraints and cascade deletes
*  **Session Management** - Token-based authentication with expiration tracking

---

## [Live URL](http://13.221.66.135:8080/)

---

## [Demo Video](https://youtu.be/f5TtbIlJzFQ?si=Szsth9hkPNaWIzUI)

---

## Repository Structure

```
Job-Application-Tracker/
├── backend/                          # backend API source code
│   ├── app/                          # app modules
│   ├── requirements.txt              # dependencies
│   ├── .env                          # configuration variables
│   ├── Dockerfile                    # Docker configuration for backend
│   └── README.md                     # backend documentation
├── frontend/                         # frontend static assets
├── nginx/                            # Nginx web server configuration
├── tests/                            # automated test suite
├── .github/                          # GitHub Actions CI/CD
│   └── workflows/
│       └── docker-build-push.yml     # Docker image build & push workflow
├── index.html                        # frontend landing page
├── docker-compose.yml                # Docker Compose configuration
├── .dockerignore                     # files Docker should ignore
├── .gitignore                        # files Git should ignore
├── docs/                             # UML diagrams & system analysis models
├── README.md                         # project overview 
└── CONTRIBUTING.md                   # contributing guidelines
```
---

## Technology Stack

| Layer                | Technology              | Version |
|----------------------|-------------------------|---------|
| **Frontend**         | HTML5, CSS3, JavaScript | Modern  |
| **Web Server**       | Nginx                   | Alpine  |
| **Backend**          | FastAPI                 | Latest  |
| **Server**           | Uvicorn                 | Latest  |
| **Database**         | SQLite                  | 3.x     |
| **Python**           | Python                  | 3.10    |
| **Containerization** | Docker                  | Latest  |
| **Orchestration**    | Docker Compose          | Latest  |
| **Testing**          | Pytest                  | 4.6.9+  |
| **CI/CD**            | GitHub Actions          | Latest  |

---

## Database Schema

### Tables Overview

1. **users** - User account information
   - user_id (PK)
   - email (UNIQUE)
   - password_hash
   - full_name
   - created_at
   - updated_at

2. **user_profiles** - Extended user profile data
   - profile_id (PK)
   - user_id (FK → users)
   - bio
   - skills (JSON)
   - location
   - phone
   - updated_at

3. **job_applications** - Job application records
   - application_id (PK)
   - user_id (FK → users)
   - job_title
   - company_name
   - application_date
   - status
   - notes
   - created_at
   - updated_at

4. **application_status_history** - Audit trail of status changes
   - history_id (PK)
   - application_id (FK → job_applications)
   - old_status
   - new_status
   - changed_at

5. **user_sessions** - Session tokens for authentication
   - session_id (PK)
   - user_id (FK → users)
   - token
   - expires_at
   - created_at

### ERD Overview

```
┌──────────────┐         ┌────────────────┐
│    users     │────┬───▶│ user_profiles  │
└──────────────┘    │    └────────────────┘
       │            │
       │            └─ (1:1 relationship)
       │
       ├──────────┐
       │          │
       ▼          ▼
  ┌─────────────────────────┐      ┌──────────────────────┐
  │  job_applications       │─────▶│ application_status   │
  │                         │      │ _history             │
  └─────────────────────────┘      └──────────────────────┘
       │
       └─ (1:N relationship)
           (Cascade Delete)
```

---

## API Server & Frontend

### Backend API

**Base URL**: `http://localhost:8080`

#### Authentication Endpoints
- `POST /register` - Register new user
- `POST /login` - User login and get JWT token
- `POST /logout` - Logout and invalidate session

#### Application Endpoints
- `POST /applications` - Create new application
- `GET /applications` - List all applications
- `GET /applications/{id}` - Get application details
- `PUT /applications/{id}` - Update application
- `DELETE /applications/{id}` - Delete application

#### Statistics Endpoints
- `GET /statistics/summary` - Overall statistics
- `GET /statistics/by-status` - Breakdown by status
- `GET /statistics/success-rate` - Success rate calculation

**API Documentation**:
- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`
- OpenAPI Schema: `http://localhost:8080/openapi.json`

### Frontend

**URL**: `http://localhost:8080`

The frontend provides:
- User registration and login interface
- Dashboard for viewing applications
- Application creation and management forms
- Status tracking and history view
- Analytics and statistics charts
- Responsive design for mobile/tablet/desktop

---

## Docker & Deployment

### Building Images Locally

```bash
# Option 1: Build both images
docker-compose build

# Option 2: Build specific image
docker-compose build app      # Backend
docker-compose build web      # Frontend (Nginx)
```

### Running with Docker Compose

```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### GitHub Actions CI/CD

The `.github/workflows/docker-build-push.yml` workflow:
- Triggers on push to `main` or `master` branches
- Builds backend and frontend Docker images
- Pushes images to Docker Hub with tags:
  - `api-latest` / `api-{commit-sha}` for backend
  - `web-latest` / `web-{commit-sha}` for frontend

**Setup Required**:
1. Add Docker Hub credentials to GitHub Secrets:
   - `DOCKERHUB_USERNAME` - Your Docker Hub username
   - `DOCKERHUB_TOKEN` - Your Docker Hub access token

2. Update image names in workflow if needed:
   - Search/replace `job-application-tracker` with your image name

### Deployment to Production

```bash
# Pull images from Docker Hub
docker pull {username}/job-application-tracker:api-latest
docker pull {username}/job-application-tracker:web-latest

# Run with docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

---

## Testing

### Test Coverage

- **Phase 1**: Unit Authentication Tests (37 tests) 
- **Phase 2**: Unit Validation Tests (45 tests) 
- **Phase 3**: Integration Tests (41 tests) 
- **Total**: 123 tests passing (100% success rate) 

### Running Tests

```bash
# Install test dependencies
cd backend
pip install -r requirements.txt

# Run all tests
python3 -m pytest tests/ -v

# Run specific test file
python3 -m pytest tests/test_unit_auth.py -v

# Run specific test
python3 -m pytest tests/test_unit_auth.py::TestPasswordValidation -v

# Run with coverage
python3 -m pytest tests/ --cov=app --cov-report=html

# Run in background (useful for CI/CD)
python3 -m pytest tests/ -v --tb=short
```

### Test Categories

**Phase 1 - Unit Auth Tests**: Password/email validation, hashing, JWT tokens
**Phase 2 - Unit Validation Tests**: Business logic, constraints, status transitions
**Phase 3 - Integration Tests**: Database operations, relationships, cascade deletes

For detailed testing documentation, see `tests/README.md`

---

## Environment

This project was developed and tested on:

<!-- ubuntu -->
<a href="https://ubuntu.com/" target="_blank"> <img height="" src="https://img.shields.io/static/v1?label=&message=Ubuntu&color=E95420&logo=Ubuntu&logoColor=E95420&labelColor=2F333A" alt="Ubuntu"></a><!-- bash --><a href="https://www.gnu.org/software/bash/" target="_blank"> <img height="" src="https://img.shields.io/static/v1?label=&message=GNU%20Bash&color=4EAA25&logo=GNU%20Bash&logoColor=4EAA25&labelColor=2F333A" alt="Bash"></a><!-- python --><a href="https://www.python.org" target="_blank"> <img height="" src="https://img.shields.io/static/v1?label=&message=Python&color=FFD43B&logo=python&logoColor=3776AB&labelColor=2F333A" alt="Python"></a><!-- fastapi --><a href="https://fastapi.tiangolo.com/" target="_blank"> <img height="" src="https://img.shields.io/static/v1?label=&message=FastAPI&color=009688&logo=fastapi&logoColor=009688&labelColor=2F333A" alt="FastAPI"></a><!-- docker -->
<a href="https://www.docker.com/" target="_blank"> <img height="" src="https://img.shields.io/static/v1?label=&message=Docker&color=2496ED&logo=docker&logoColor=2496ED&labelColor=2F333A" alt="Docker"></a><!-- vs code -->
<a href="https://code.visualstudio.com/" target="_blank"> <img height="" src="https://img.shields.io/static/v1?label=&message=VS%20Code&color=5C2D91&logo=Visual%20Studio%20Code&logoColor=5C2D91&labelColor=2F333A" alt="VS Code"></a><!-- git -->
<a href="https://git-scm.com/" target="_blank"> <img height="" src="https://img.shields.io/static/v1?label=&message=Git&color=F05032&logo=Git&logoColor=F05032&labelColor=2F333A" alt="Git"></a><!-- github -->
<a href="https://github.com" target="_blank"> <img height="" src="https://img.shields.io/static/v1?label=&message=GitHub&color=181717&logo=GitHub&logoColor=f2f2f2&labelColor=2F333A" alt="GitHub"></a>

---

## Setup Instructions

### Prerequisites

- Python 3.10+
- Docker & Docker Compose (for containerized setup)
- Git
- Node.js (optional, for frontend development)

### Local Development Setup

#### 1. Clone the Repository

```bash
git clone https://github.com/m-dhieu/Job-Application_Tracker.git
cd Job-Application_Tracker
```

#### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration
```

#### 3. Start Backend Server

```bash
# From backend directory with venv activated
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

The backend will be available at `http://localhost:8080`

#### 4. Run Tests

```bash
# From project root or backend directory
python3 -m pytest tests/ -v
```

### Docker Setup (Recommended)

#### 1. Start All Services

```bash
# From project root
docker-compose up --build
```

#### 2. Access Services

- **Frontend**: `http://localhost:8080`
- **API Docs**: `http://localhost:8080/docs`
- **ReDoc**: `http://localhost:8080/redoc`

#### 3. Stop Services

```bash
docker-compose down
```

---

## Next Steps After Setup

### 1. Access the Backend API

After starting the backend, open your browser and navigate to:

```
http://localhost:8080/docs
```

Here you can:
- Explore all available REST API endpoints
- Test endpoints interactively
- View request/response schemas
- Generate client code

### 2. Use the Frontend Dashboard

Navigate to:

```
http://localhost:8080
```

Here you can:
- Register a new account
- Create and manage job applications
- Track application status
- View analytics and statistics
- Monitor your job search progress

### 3. Example Workflow

```bash
# 1. Register User (via Frontend or API)
POST /register
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "Monica Dhieu"
}

# 2. Login
POST /login
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
# Returns: {"access_token": "..."}

# 3. Create Application
POST /applications
{
  "job_title": "Software Engineer",
  "company_name": "TechCorp",
  "status": "applied"
}

# 4. Update Application
PUT /applications/1
{
  "status": "interview_scheduled"
}

# 5. View Statistics
GET /statistics/summary
```

### 4. Run Tests

```bash
python3 -m pytest tests/ -v
```

Expected output: `123 passed in 16.58 seconds`

### 5. View Logs

```bash
# Docker Compose logs
docker-compose logs -f

# Backend logs
docker-compose logs -f app

# Frontend/Nginx logs
docker-compose logs -f web
```

---

## Development Workflow

### Branch Strategy

- `main` - Production-ready code
- `develop` - Development branch
- `feature/*` - Feature branches
- `bugfix/*` - Bug fix branches

### Making Changes

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and test
python3 -m pytest tests/ -v

# Commit changes
git add .
git commit -m "Add new feature"

# Push to GitHub
git push origin feature/new-feature

# Create Pull Request on GitHub
```

### Code Style

- Python: Follow [PEP8](https://pep8.org/)
- Use [pycodestyle](https://pypi.org/project/pycodestyle/) for linting
- Format code with [Black](https://github.com/psf/black)

```bash
# Run linter
pycodestyle backend/app/

# Format code
black backend/app/
```

---

## Troubleshooting

### Issue: Port Already in Use

**Error**: `Address already in use`

**Solution**:
```bash
# Find process using port 8080
lsof -i :8080

# Kill process
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8000
```

### Issue: Docker Build Fails

**Error**: `failed to build image`

**Solution**:
```bash
# Clean up Docker
docker system prune -a

# Rebuild
docker-compose build --no-cache
```

### Issue: Database Connection Error

**Error**: `Cannot connect to database`

**Solution**:
```bash
# Verify database file exists
ls -la backend/job_tracker.db

# Check .env file
cat backend/.env

# Verify permissions
chmod 755 backend/
```

### Issue: Tests Failing

**Error**: `Failed test cases`

**Solution**:
```bash
# Run specific test with verbose output
python3 -m pytest tests/test_file.py -v -s

# Run with full traceback
python3 -m pytest tests/ -v --tb=long

# Check test logs
tail -100 tests/test_results_*.txt
```

### Issue: Docker Images Not Pushing

**Error**: `authentication failed`

**Solution**:
1. Verify Docker Hub credentials are correct
2. Check GitHub Secrets are set:
   - `DOCKERHUB_USERNAME`
   - `DOCKERHUB_TOKEN`
3. Verify workflow file syntax:
   ```bash
   cd .github/workflows
   cat docker-build-push.yml
   ```
4. Check GitHub Actions logs in repository Settings

---

## Team

<details>
<summary> Monica Dhieu -- Backend & Full Stack Developer</summary>
<ul>
<li><a href="https://github.com/m-dhieu">GitHub</a></li>
<li><a href="https://www.linkedin.com/in/monica-dhieu/">LinkedIn</a></li>
<li><a href="mailto:monicadhieu@example.com">Email</a></li>
</ul>
</details>

---

## Contributing

Contributions, issues, and feature requests are welcome!

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes
4. Run tests (`python3 -m pytest tests/ -v`)
5. Commit your changes (`git commit -m 'Add AmazingFeature'`)
6. Push to the branch (`git push origin feature/AmazingFeature`)
7. Open a Pull Request

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for more details.

---

## License

MIT License - see LICENSE file for details

---

## Contact

For questions, issues, or suggestions:

- **GitHub Issues**: [Create an Issue](https://github.com/yourusername/Job-Application-Tracker/issues)
- **Email**: monicadhieu@example.com
- **LinkedIn**: [Monica Dhieu](https://www.linkedin.com/in/monica-dhieu/)

---

## Roadmap

- [ ] Phase 4: API Endpoint Tests (50 tests) - Authentication & Application endpoints
- [ ] Phase 5: End-to-End Tests (15 tests) - Complete user workflows
- [ ] Admin Dashboard: Create admin dashboard
- [ ] Mobile App: React Native mobile application & push notifications
- [ ] Advanced Analytics: ML-based insights and recommendations
- [ ] Integrations: LinkedIn, Indeed API integrations, Recruiter ATR integration
- [ ] Database: Scale to PostgreSQL

---

## Changelog

### Version 1.0.0

-  Initial project setup
-  Backend API with FastAPI
-  SQLite database with 5 tables
-  User authentication and JWT tokens
-  Job application management
-  Status tracking and audit trails
-  Frontend interface
-  Docker containerization
-  Nginx web server configuration
-  GitHub Actions CI/CD workflow
-  123 comprehensive tests (100% passing)

---

*Last Updated: March 31, 2026*
