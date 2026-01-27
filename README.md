# Wand 🪄

**Wand** is an intelligent AI-powered career assistant that helps users analyze job postings, optimize their resumes, and generate tailored cover letters. It leverages advanced LLMs (Gemini 2.5 Pro & Flash) to provide deep insights and actionable feedback.

## 🚀 Features

- **Job Analysis**: deeply analyzes job descriptions to extract requirements, skills, and expected salary.
- **Resume Parsing**: Extracts structured data from PDF resumes using AI.
- **Gap Analysis**: Compares your resume against job requirements to identify missing qualifications and keywords.
- **Resume Optimization**: Provides specific "Add", "Update", or "Delete" suggestions to tailor your resume.
- **Cover Letter Generation**: improved cover letters (Professional, Creative, Storytelling modes) tailored to the specific job.
- **Application Tracking**: Kanban-style board to track job applications.

## 🏗️ Architecture

The project is organized into three main components:

### 1. Frontend (`/frontend`)
The user interface built with **Next.js 14**, **TypeScript**, and **Tailwind CSS**.
- **Tech Stack**: Next.js, React, Zustand (State Management), Framer Motion (Animations).
- **Key Functionality**: Job dashboard, interactive resume editor, analysis visualization, real-time updates via WebSockets.

### 2. API (`/api`)
The backend REST API built with **FastAPI**.
- **Tech Stack**: FastAPI, SQLAlchemy (SQLite), Pydantic.
- **Key Functionality**: Data persistence, request orchestration, file handling, and communication with the Engine.
- **Workers**: Uses Celery (with Redis) for background processing of long-running analysis tasks.

### 3. Engine (`/engine`)
The intelligence core of the application.
- **Tech Stack**: Python, Inspector (Structured Output), PyMuPDF.
- **AI Models**:
    - **Gemini 2.5 Pro**: Used for complex reasoning (Qualification Validation, Cover Letter Writing).
    - **Gemini 2.5 Flash**: Used for high-speed tasks (Parsing, Formatting Checks, Keyword Matching).
- **Modules**:
    - `job/parser`: Extracts structured job data.
    - `analysis/qualification_check`: validatates resume claims against requirements.
    - `analysis/formatting_check`: Reviews resume formatting and chronology.
    - `cover_letter/generator`: Generates personalized cover letters.

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- Redis (for background tasks)
- Google Gemini API Key

### Backend Setup
1. Navigate to root directory.
2. Create virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set environment variables in `.env`:
   ```env
   GEMINI_API_KEY=your_key_here
   REDIS_URL=redis://localhost:6379/0
   ```
5. Start the server:
   ```bash
   uvicorn api.main:app --reload
   ```

### Frontend Setup
1. Navigate to frontend:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start dev server:
   ```bash
   npm run dev
   ```

## 🧠 AI Model Configuration

The system uses a hybrid model approach for optimal performance:
- **Gemini 2.5 Pro**: used for logic-heavy tasks requiring "reasoning" capabilities.
- **Gemini 2.5 Flash**: Used for speed-critical extraction and matching tasks.

## 📄 License
MIT
