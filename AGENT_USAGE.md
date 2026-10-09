# AI Agent Usage

## Tools used
- Internal Coding Agent System (Gemini-powered coding assistant)

## Representative prompts
The instructions provided by the user were extremely detailed and structured, serving as the main prompt. The agent parsed these instructions into an implementation plan and followed them step-by-step.

- "we have to follow clean coding and standard concept to achieve specific feature and follow single responsibility"
- (Implicit prompt via task checklist for creating services, schemas, and models in a structured way).

## Delegated work
The agent generated the entire backend structure:
- **Project Scaffold**: Created folders (`app/api`, `app/core`, `app/models`, `app/schemas`, `app/services`, `app/workers`).
- **Database Schema**: Wrote SQLAlchemy models (`GenerationJob`, `Certificate`) and configured Alembic.
- **API Endpoints**: Wrote FastAPI routers for Jobs and Certificates, matching the OpenAPI specs requested.
- **PDF Generation**: Wrote the ReportLab script in `CertificateGenerator` and properly encapsulated it.
- **Background Processing**: Implemented `CertificateWorker` to process certificates independently without stopping the job on partial failure.
- **Testing & Deployment**: Generated `pytest` cases, `Dockerfile`, and `docker-compose.yml`.

## Mistakes
- In the initial setup on Windows, `psycopg2-binary` failed to build from source because it lacked the pg_config executable. The agent recognized the build failure and switched to `psycopg-binary` which provides modern pre-built wheels and is recommended for SQLAlchemy 2.x.
- A minor package collision occurred with `pydantic-core` failing to build on Python 3.14 via `pip`. The agent relaxed strict version pinning to allow fetching compatible dependencies.
- The `alembic init` command failed initially because the virtual environment activation and dependency installation didn't finish properly.

## Verification
- Code review performed during generation to ensure logic adhered to the separation of concerns (e.g., PDF generation isolated in a service, not in controllers).
- Verified failure isolation in the background worker via the `try/except` loop over individual certificates, rolling back DB sessions correctly on failure so that subsequent generations are not broken.
- Pytest cases check API status and validation rules.
