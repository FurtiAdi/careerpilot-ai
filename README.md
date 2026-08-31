# CareerPilot AI

CareerPilot AI is an AI-powered career assistant that helps users evaluate how well their skills match a job description.

The application combines deterministic skill matching with AI-generated career guidance.

## Features

- User registration and login
- JWT-based authentication
- Resume PDF upload
- Resume text extraction
- Skill extraction and normalization
- Required vs preferred skill classification
- Weighted job-match scoring
- Matched and missing skill breakdown
- AI-generated analysis and recommendations
- Analysis history
- User profile and profile statistics
- Profile picture upload
- Protected resume and profile resources

## Tech Stack

### Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS

### Backend

- FastAPI
- Python
- SQLAlchemy
- Alembic
- PyMuPDF
- JWT authentication

### Database

- PostgreSQL

### AI

- OpenAI API

## Project Structure

```text
careerpilot-ai/
├── backend/
│   ├── alembic/
│   ├── app/
│   │   ├── core/
│   │   ├── database/
│   │   ├── dependencies/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── services/
│   │   └── skills/
│   ├── tests/
│   ├── .env.example
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── .env.example
│   └── package.json
│
└── README.md

## Prerequisites

Install:

- Python
- Node.js
- PostgreSQL
- Git

## Backend Setup

From the project root:

```bash
cd backend
```

Create a virtual environment:

```bash
python3 -m venv venv
```

Activate it on macOS/Linux:

```bash
source venv/bin/activate
```

Install backend dependencies:

```bash
pip install -r requirements.txt
```

Create your backend environment file:

```bash
cp .env.example .env
```

Update `.env` with your PostgreSQL credentials, JWT secret, and OpenAI API key.

Example:

```env
POSTGRES_USER=careerpilot
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=careerpilot_db

SECRET_KEY=your_secure_secret_key

OPENAI_API_KEY=your_openai_api_key
```

## Database Setup

Create the PostgreSQL user and database if they do not already exist.

Example database creation:

```bash
createdb -O careerpilot careerpilot_db
```

Apply database migrations:

```bash
alembic upgrade head
```

Check the current migration version:

```bash
alembic current
```

Alembic is the authoritative database schema management system for the project.

## Run the Backend

From the `backend` directory:

```bash
uvicorn app.main:app --reload
```

The backend API will run at:

```text
http://127.0.0.1:8000
```

FastAPI interactive documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## Frontend Setup

Open another terminal and go to the frontend directory:

```bash
cd frontend
```

Install frontend dependencies:

```bash
npm install
```

Create the frontend environment file:

```bash
cp .env.example .env.local
```

The default local API configuration is:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

Start the frontend development server:

```bash
npm run dev
```

Open the application in your browser:

```text
http://localhost:3000
```

## Running Tests

From the `backend` directory:

```bash
pytest -v
```

The Phase 1 backend test suite covers:

- Authentication
- Authentication dependencies
- Authentication routes
- Skill extraction
- Skill normalization
- Required and preferred skill classification
- Deterministic match scoring
- AI analysis behavior
- Analysis services
- Analysis routes
- PDF upload validation
- Profile image validation
- Profile routes
- Protected resume and profile resources
- Database rollback behavior

## Frontend Production Build

From the `frontend` directory:

```bash
npm run build
```

This runs the Next.js production build and TypeScript validation.

## How Job Analysis Works

1. The user registers or logs in.
2. The user uploads a resume or provides candidate skills.
3. CareerPilot extracts and normalizes candidate skills.
4. The job description is analyzed to identify required and preferred skills.
5. A deterministic weighted match score is calculated.
6. Matched and missing skills are returned.
7. OpenAI generates structured career guidance based on the deterministic result.
8. The completed analysis is stored in the authenticated user's analysis history.
9. The user can review previous analyses from the History page.

## Skill Matching

CareerPilot uses deterministic matching before AI analysis.

The matching process includes:

- Normalized skill names
- Skill aliases
- Required skill classification
- Preferred skill classification
- Matched required skills
- Missing required skills
- Matched preferred skills
- Missing preferred skills
- Weighted match scoring

This keeps the numerical job-match score predictable and explainable.

## AI Analysis

AI-generated recommendations are based on the deterministic skill-match result.

The AI layer provides structured output such as:

- Summary
- Strengths
- Missing requirements
- Recommendations

If the AI provider is temporarily unavailable, the deterministic match results remain available to the user.

## Authentication

CareerPilot uses JWT-based authentication.

Protected endpoints require a valid bearer token.

Authentication is used to protect:

- Job analyses
- Analysis history
- Profile information
- Profile statistics
- Resume access
- Profile picture access

User-owned resources are scoped to the authenticated user.

## Upload Validation

### Resume Uploads

Resume uploads:

- Must be PDF files
- Must use the expected PDF content type
- Must not be empty
- Must stay within the configured size limit
- Must contain a valid PDF file signature

### Profile Pictures

Profile pictures:

- Support JPEG
- Support PNG
- Support WebP
- Have a maximum upload size
- Are checked using MIME type
- Are checked using file signatures
- Use UUID-based filenames

Uploaded files are stored outside Git tracking.

## Profile Features

The profile page includes:

- User name
- Email
- Profile picture
- Resume availability
- Total analyses
- Average match score
- Recent analyses

Users can also upload a new profile picture.

When a profile picture is replaced, the previous image is removed from local storage.

## Analysis History

Authenticated users can:

- View their previous job analyses
- See previous match scores
- Delete analyses they own

Analysis queries are scoped by the authenticated user's ID.

## Error Handling

The frontend uses centralized API error handling.

Expected behavior includes:

- Authentication failures redirect to the login page
- API errors are displayed to users
- Loading states are shown while requests are running
- Empty states are shown when no data exists
- Invalid uploads display backend validation messages

The backend also includes a global unexpected-error handler for server-side failures.

## Configuration

Backend configuration is centralized in:

```text
backend/app/core/config.py
```

It includes settings for:

- PostgreSQL
- JWT authentication
- OpenAI
- Upload directories
- CORS origins

Frontend API configuration uses:

```env
NEXT_PUBLIC_API_URL
```

## Database Migrations

CareerPilot uses Alembic for database schema management.

Apply all migrations with:

```bash
alembic upgrade head
```

Check the current revision with:

```bash
alembic current
```

A fresh database can be initialized completely through Alembic migrations.

## Security and Validation

CareerPilot includes:

- Password hashing
- JWT authentication
- Protected API endpoints
- User-scoped resources
- Environment-based secrets
- PDF validation
- Image validation
- File-size limits
- UUID-based upload filenames
- Safe upload paths
- Database rollback handling
- Alembic migrations
- Centralized API error handling

## Phase 1 Status

Phase 1 focuses on building a reliable MVP foundation.

Completed Phase 1 areas include:

- Authentication
- Resume intelligence
- Skill extraction
- Skill normalization
- Deterministic job matching
- Required vs preferred skill classification
- Explainable match scoring
- Structured AI analysis
- Analysis history
- User profile
- Upload validation
- Protected resources
- Database migrations
- Centralized configuration
- Backend automated tests
- Frontend loading and error states
- Environment configuration examples

## Development Workflow

Typical backend workflow:

```bash
cd backend
source venv/bin/activate
alembic upgrade head
pytest -v
uvicorn app.main:app --reload
```

Typical frontend workflow:

```bash
cd frontend
npm install
npm run dev
```

Before committing frontend changes:

```bash
npm run build
```

Before committing backend changes:

```bash
pytest -v
```

## Development Notes

Local environment files and uploaded user files are excluded from Git.

Never commit:

```text
.env
.env.local
backend/uploads/
```

Do not commit real:

- Database passwords
- JWT secret keys
- OpenAI API keys

Use `.env.example` files to document required configuration instead.

## Current Phase 1 Validation

Before considering Phase 1 complete, verify:

- Backend tests pass
- Frontend production build passes
- Database migrations work on a fresh database
- Registration works
- Login works
- Resume upload works
- Skill extraction works
- Job analysis works
- AI analysis works or falls back safely
- Analysis history works
- Analysis deletion works
- Profile loads
- Profile picture upload works
- Profile statistics work
- Protected resources require authentication
- Logout and expired-token behavior work