# Required Services for Wand

To run the Wand application, you need **4 services** running simultaneously:

## 1. **Backend API** (FastAPI)
```bash
cd /Users/nishant/Desktop/wand
uvicorn api.main:app --reload
```
- **Port**: 8000
- **Purpose**: Main API server for all backend operations
- **Status**: ✅ Currently running

## 2. **Frontend** (Next.js)
```bash
cd /Users/nishant/Desktop/wand/frontend
npm run dev
```
- **Port**: 3000
- **Purpose**: User interface
- **Status**: ✅ Currently running

## 3. **Redis** (Message Broker & Result Backend)
```bash
brew services start redis
```
- **Port**: 6379
- **Purpose**: Queue broker for Celery tasks
- **Status**: ✅ Currently running
- **Note**: Runs as a background service via Homebrew

## 4. **Celery Worker** (Background Task Processor)
```bash
cd /Users/nishant/Desktop/wand
celery -A api.celery_app worker --loglevel=info
```
- **Purpose**: Processes job analysis tasks asynchronously
- **Status**: ✅ Currently running
- **Concurrency**: 3 workers

---

## Quick Start (All Services)

```bash
# Terminal 1: Backend
cd /Users/nishant/Desktop/wand
uvicorn api.main:app --reload

# Terminal 2: Frontend
cd /Users/nishant/Desktop/wand/frontend
npm run dev

# Terminal 3: Redis (one-time setup, then runs in background)
brew services start redis

# Terminal 4: Celery Worker
cd /Users/nishant/Desktop/wand
celery -A api.celery_app worker --loglevel=info
```

---

## Checking Service Status

### Redis
```bash
brew services list | grep redis
```

### Celery Worker
```bash
ps aux | grep celery
```

### Backend/Frontend
Check the terminal windows where they're running.

---

## Stopping Services

### Redis
```bash
brew services stop redis
```

### Celery Worker
Press `Ctrl+C` in the terminal running the worker.

### Backend/Frontend
Press `Ctrl+C` in their respective terminals.
