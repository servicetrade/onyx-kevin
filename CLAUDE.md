# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Onyx (formerly Danswer) is an open-source Gen-AI enterprise search platform built with:
- **Frontend**: Next.js 15 with TypeScript, React 18, Tailwind CSS, Radix UI components, and shadcn/ui
- **Backend**: Python 3.11 with FastAPI, SQLAlchemy, Alembic, and Celery
- **External Services**: PostgreSQL (relational DB), Vespa (vector DB/search), Redis (cache)
- **UI Components**: Radix UI primitives, Headless UI, Tailwind CSS with custom theming
- **State Management**: SWR for data fetching/caching, React Context for global state

## Development Commands

### Backend (Python)

```bash
# Setup virtual environment (Python 3.11 required)
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements/default.txt
pip install -r backend/requirements/dev.txt
pip install -r backend/requirements/ee.txt
pip install -r backend/requirements/model_server.txt

# Install Playwright for Web Connector
playwright install

# Run database migrations
cd backend && alembic upgrade head

# Start services (from backend directory)
uvicorn model_server.main:app --reload --port 9000                    # Model server
python ./scripts/dev_run_background_jobs.py                           # Background jobs
AUTH_TYPE=disabled uvicorn onyx.main:app --reload --port 8080        # API server

# Run tests
cd backend && pytest                    # Run all tests
pytest tests/unit/                      # Run unit tests only
pytest tests/integration/               # Run integration tests only
pytest -k "test_name"                   # Run specific test
pytest -m slow                          # Run tests marked as slow

# Linting and type checking
cd backend
pre-commit install  # One-time setup
python -m mypy .    # Type checking
ruff check .        # Linting (configured in pyproject.toml)
```

### Frontend (Next.js)

```bash
# Install dependencies
cd web && npm i

# Development server
npm run dev

# Build production
npm run build

# Linting
npm run lint
npm run lint:unused         # Check unused imports
npm run lint:fix-unused     # Fix unused imports

# Run tests
npm test

# Format code (Prettier 2.8.8)
npx prettier --write .
```

### Docker Development

```bash
# Start external services only (Postgres, Vespa, Redis)
cd deployment/docker_compose
docker compose -f docker-compose.dev.yml -p onyx-stack up -d index relational_db cache

# Full stack with containers
docker compose -f docker-compose.dev.yml -p onyx-stack up -d
```

## Architecture Overview

### Backend Structure
- `backend/onyx/` - Core application code
  - `main.py` - FastAPI application entry point with lifespan management, CORS, error handling
  - `auth/` - Authentication and authorization (fastapi-users, OAuth2, SAML)
  - `chat/` - Chat interface and LLM interactions
  - `connectors/` - 40+ data source connectors (Google Drive, Slack, Confluence, etc.)
  - `db/` - Database models (SQLAlchemy) and queries
  - `document_index/` - Document indexing and search (Vespa integration)
  - `llm/` - LLM provider integrations (OpenAI, Anthropic, etc.)
  - `agents/` - AI agent implementations
  - `background/` - Celery background tasks for async operations
  - `server/` - API route handlers organized by feature
  - `prompts/` - LLM prompt templates and management
  - `redis/` - Redis cache and key-value store utilities
  - `file_processing/` - Document parsing and processing
  - `natural_language_processing/` - NLP utilities and embeddings
  - `tools/` - Custom tools for AI agents
  - `utils/` - Shared utilities and helpers

- `backend/alembic/` - Database migrations (main)
- `backend/alembic_tenants/` - Database migrations (multi-tenant)
- `backend/ee/` - Enterprise Edition features
- `backend/model_server/` - Local NLP model server (embeddings, reranking)
- `backend/scripts/` - Development and utility scripts

### Frontend Structure
- `web/src/app/` - Next.js app router pages (using App Router, not Pages Router)
- `web/src/components/` - Reusable React components
- `web/src/lib/` - Utilities and API client code
  - `lib/generated/` - OpenAPI generated types
- `web/src/hooks/` - Custom React hooks
- `web/src/services/` - Frontend service layer

### Key Patterns

**API Communication**: Frontend communicates with backend via REST API on port 8080. OpenAPI schema is generated and types are shared. Next.js rewrites `/api/docs` and `/openapi.json` to backend endpoints.

**Authentication**: Supports multiple auth types (disabled, basic, OIDC, SAML). Set via `AUTH_TYPE` environment variable. Uses fastapi-users for user management.

**Background Jobs**: Long-running tasks are handled by Celery workers using Redis as the message broker. Start with `backend/scripts/dev_run_background_jobs.py` for development.

**Document Processing**: Documents are indexed into Vespa for vector search and PostgreSQL for metadata. The indexing pipeline is in `backend/onyx/indexing/`.

**Connectors**: 40+ data source connectors in `backend/onyx/connectors/`. Each connector implements a standard interface for fetching and indexing documents. See `backend/onyx/connectors/README.md` for details on adding new connectors.

**Multi-tenancy**: Enterprise Edition supports multi-tenant deployments with separate schemas per tenant. Migrations are in `backend/alembic_tenants/`.

## Testing Approach

- **Backend**: pytest with fixtures in conftest.py files
  - Unit tests: `backend/tests/unit/`
  - Integration tests: `backend/tests/integration/`
  - Daily connector tests: `backend/tests/daily/`
  - Test markers: `@pytest.mark.slow` for long-running tests
  - Python path includes `generated/onyx_openapi_client` for API client tests
- **Frontend**: Jest for unit tests, Playwright for E2E tests
  - Unit tests: Run with `npm test`
  - E2E tests: Use Playwright with `@playwright/test`

## Key Configuration Files

- `backend/pyproject.toml` - Python project config (mypy, ruff)
- `backend/pytest.ini` - pytest configuration with pythonpath and markers
- `backend/alembic.ini` - Alembic migrations configuration
- `web/tsconfig.json` - TypeScript configuration with `@/*` path alias
- `web/components.json` - shadcn/ui component configuration
- `web/next.config.js` - Next.js configuration with Sentry, rewrites, CSP headers
- `.pre-commit-config.yaml` - Pre-commit hooks (black, reorder-python-imports, autoflake, ruff, prettier)

## Development Tips

1. **Python Version**: Always use Python 3.11 - higher versions may have library compatibility issues
2. **Virtual Environment**: Create venv outside the project directory to avoid mypy issues
3. **Debugging**: Use `LOG_LEVEL=DEBUG` environment variable for detailed logging
4. **Frontend Imports**: Path alias `@/` maps to `src/` directory (configured in tsconfig.json)
5. **Type Safety**: Backend follows strict typing with mypy - all code must be fully type-annotated
6. **Pre-commit Hooks**: Run `pre-commit install` once after cloning (uses black, reorder-python-imports, autoflake, ruff, prettier)
7. **Frontend Formatting**: Use Prettier 2.8.8 - run `npx prettier --write .` from web directory
8. **Database Migrations**:
   - Main DB: Use `alembic upgrade head` from backend directory
   - Multi-tenant: Use `alembic_tenants` for tenant-specific migrations
9. **Background Jobs**: Development script is at `backend/scripts/dev_run_background_jobs.py`
10. **Windows Users**: Use PowerShell-compatible commands (see CONTRIBUTING.md for Windows-specific examples)

## Staging Server Deployment

**Server location**: `/root/danswer/deployment/docker_compose`

**Key facts**:
- Uses pre-built Docker images (`onyxdotapp/onyx-backend:latest`), NOT local code
- To deploy code changes: must rebuild image with `docker build -t onyxdotapp/onyx-backend:latest -f backend/Dockerfile backend/`
- Database is `postgres` (not `danswer`) in the postgres container
- Use `docker-compose` (with hyphen) not `docker compose`
- Restart script: `./restart-onyx.sh`

**Alembic migrations**:
- NEVER create migrations with duplicate `down_revision` values - causes "multiple heads" error
- Check heads before creating: `docker run --rm <image> alembic heads`
- If stuck, can run SQL directly against database instead of migrations

**Docker exec commands**:
- When running Python via `docker exec`, use single-line format with semicolons
- Multi-line Python with indentation breaks when pasted into shell
- Good: `docker exec -it container python -c "import boto3; client = boto3.client('bedrock'); print(client)"`
- Bad: Multi-line with indentation (causes `IndentationError: unexpected indent`)