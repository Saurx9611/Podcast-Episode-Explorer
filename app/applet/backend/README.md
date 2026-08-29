# Podcast Explorer Backend

FastAPI backend for Podcast Explorer. It uses PostgreSQL + pgvector for semantic search over transcript segments.

## Prerequisites
- Python 3.10+
- PostgreSQL with `pgvector` extension installed
- Node.js (for the Next.js frontend)

## Environment Setup

Copy `.env.example` to `.env` and configure your settings.

```bash
cp .env.example .env
```

## Setup PostgreSQL

1. Install PostgreSQL and `pgvector`:
   ```bash
   # Example for Ubuntu/Debian
   sudo apt install postgresql postgresql-contrib postgresql-server-dev-all
   cd /tmp
   git clone --branch v0.7.0 https://github.com/pgvector/pgvector.git
   cd pgvector
   make
   sudo make install
   ```

2. Create the database and user (or run locally):
   ```sql
   CREATE DATABASE podcast_explorer;
   CREATE USER postgres WITH ENCRYPTED PASSWORD 'postgres';
   GRANT ALL PRIVILEGES ON DATABASE podcast_explorer TO postgres;
   
   -- Connect to the DB
   \c podcast_explorer;
   
   -- Enable pgvector
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

## Running the Backend

1. Install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r backend/requirements.txt
   ```

2. Run Database Migrations:
   ```bash
   alembic upgrade head
   ```

3. Seed Data (Optional for development):
   ```bash
   python3 backend/seed.py
   ```

4. Start FastAPI:
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```

## Starting the Frontend

1. Ensure `NEXT_PUBLIC_API_URL` is set in the frontend `.env.local`:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000/api
   ```

2. Run Next.js:
   ```bash
   npm run dev
   ```

## API Architecture
- `POST /api/episodes`: Upload audio, creates episode + processing job.
- `GET /api/search`: PGVector semantic search on transcript segments.
- `POST /api/search/saved`: Save search filters and queries.

## AI Provider Configuration
Services under `backend/services` implement abstractions for Transcription, Diarization, Chunking, and Embeddings. 
Replace the mock implementations (`MockTranscriptionService`, etc.) with real providers (e.g. OpenAI Whisper, Azure, HuggingFace) by modifying the service classes and loading API keys via `core/config.py`.
