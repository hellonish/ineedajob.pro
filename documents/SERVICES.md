# Required Services for Wand

To run the Wand application locally, you need two services:

## 1. Backend API (FastAPI)

```bash
cd /Users/nishant/Desktop/wand
uvicorn api.main:app --reload
```

- Port: 8000
- Purpose: API routes, auth, persistence, file handling, background orchestration, and WebSocket events

## 2. Frontend (Next.js)

```bash
cd /Users/nishant/Desktop/wand/frontend
npm run dev
```

- Port: 3000
- Purpose: Browser UI

## Quick Start

```bash
./start_services.sh
```

## Stopping Services

```bash
./stop_services.sh
```
