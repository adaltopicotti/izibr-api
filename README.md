# Instructor Platform Backend

Robust backend for a private driving instructor platform built with Python (FastAPI) and SQLAlchemy.

## Features

- **FastAPI**: High performance, easy to learn, fast to code, ready for production.
- **SQLAlchemy (Async)**: Database ORM with support for PostgreSQL (Production) and SQLite (Dev).
- **Authentication**: JWT based auth with `passlib` and `python-jose`. Structure ready for Google OAuth2.
- **Dependency Management**: Uses `uv` for blazing fast package management.
- **Docker & Cloud Run**: Ready for containerized deployment.

## Local Development

1. **Install `uv`**:
   ```bash
   pip install uv
   ```

2. **Install Dependencies**:
   ```bash
   uv sync
   ```

3. **Run the Application**:
   ```bash
   uv run uvicorn app.main:app --reload
   ```
   The API will be available at `http://localhost:8000`.

4. **Run Tests**:
   ```bash
   uv run pytest
   ```

## Deployment to Google Cloud Run (GitHub Actions)

This repository includes a GitHub Actions workflow to automatically deploy to Cloud Run on push to `main`.

### Prerequisites

1. **Google Cloud Project**: Create a GCP project.
2. **Artifact Registry**: Create a Docker repository in Artifact Registry (e.g., named `instructor-repo`).
3. **Cloud Run**: Enable the Cloud Run API.
4. **Service Account**: Create a service account with permissions:
   - `Cloud Run Admin`
   - `Service Account User`
   - `Artifact Registry Writer`
   - `Storage Admin` (if needed for container building)

### GitHub Secrets Configuration

Go to your GitHub Repository -> Settings -> Secrets and Variables -> Actions, and add the following:

- `GCP_PROJECT_ID`: Your Google Cloud Project ID.
- `GCP_SA_KEY`: The JSON key of your Service Account.
- `DATABASE_URL`: The connection string for your Production PostgreSQL database (e.g., `postgresql+asyncpg://user:pass@host/dbname`).
- `SECRET_KEY`: A strong secret key for JWT generation.

### Workflow Details

The workflow is located in `.github/workflows/deploy.yml`. It performs the following:
1. Authenticates with Google Cloud.
2. Builds the Docker image.
3. Pushes the image to Google Artifact Registry.
4. Deploys the image to Cloud Run.

**Note**: You may need to adjust the `REGION` and `REPO_NAME` env variables in `.github/workflows/deploy.yml` to match your GCP setup.
