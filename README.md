# Nyaysetu

A full-stack web application built with **Next.js** (frontend) and **FastAPI** (backend).

---

## Project Structure

```
Nyaysetu/
├── frontend/                  # Next.js App Router + Tailwind CSS + shadcn/ui
│   ├── src/
│   │   ├── app/               # App Router pages and layouts
│   │   │   ├── layout.tsx     # Root layout
│   │   │   ├── page.tsx       # Home page
│   │   │   └── globals.css    # Global styles (Tailwind + shadcn theme)
│   │   ├── components/
│   │   │   └── ui/            # shadcn/ui components (auto-generated)
│   │   │       └── button.tsx
│   │   └── lib/
│   │       └── utils.ts       # Utility functions (cn helper, etc.)
│   ├── public/                # Static assets
│   ├── components.json        # shadcn/ui configuration
│   ├── next.config.ts         # Next.js configuration
│   ├── postcss.config.mjs     # PostCSS config (Tailwind v4)
│   ├── tsconfig.json          # TypeScript configuration
│   ├── eslint.config.mjs      # ESLint configuration
│   └── package.json           # Node.js dependencies and scripts
│
├── backend/                   # FastAPI REST API
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # Application entry point (CORS, routers)
│   │   └── routers/
│   │       ├── __init__.py
│   │       └── health.py      # Health-check endpoint
│   ├── venv/                  # Python virtual environment (gitignored)
│   ├── requirements.txt       # Python dependencies
│   └── .env.example           # Environment variable template
│
├── .gitignore                 # Root-level gitignore
└── README.md                  # This file
```

---

## Tech Stack

| Layer     | Technology                                      |
| --------- | ----------------------------------------------- |
| Frontend  | Next.js 16 (App Router), React 19, TypeScript   |
| Styling   | Tailwind CSS v4, shadcn/ui                      |
| Backend   | FastAPI, Uvicorn, Pydantic v2                    |
| Language  | TypeScript (frontend), Python 3.14 (backend)    |

---

## Getting Started

### Prerequisites

- **Node.js** ≥ 20 LTS and **npm**
- **Python** ≥ 3.10

### 1. Frontend

```bash
cd frontend
npm install        # Install dependencies (already done on init)
npm run dev        # Start dev server on http://localhost:3000
```

### 2. Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env

# Run the development server
uvicorn app.main:app --reload --port 8000
```

The API will be available at **http://localhost:8000** with interactive docs at **http://localhost:8000/docs**.

---

## Available Scripts

### Frontend (`frontend/`)

| Command           | Description                      |
| ----------------- | -------------------------------- |
| `npm run dev`     | Start Next.js development server |
| `npm run build`   | Create production build          |
| `npm run start`   | Start production server          |
| `npm run lint`    | Run ESLint                       |

### Backend (`backend/`)

| Command                                          | Description                     |
| ------------------------------------------------ | ------------------------------- |
| `uvicorn app.main:app --reload`                  | Start FastAPI with hot reload   |
| `pip install -r requirements.txt`                | Install dependencies            |

---

## Adding shadcn/ui Components

shadcn/ui is already initialized. To add more components:

```bash
cd frontend
npx shadcn@latest add <component-name>

# Examples:
npx shadcn@latest add card
npx shadcn@latest add dialog
npx shadcn@latest add input
```

Browse available components at [ui.shadcn.com](https://ui.shadcn.com/docs/components).

---

## API Endpoints

| Method | Path           | Description            |
| ------ | -------------- | ---------------------- |
| GET    | `/`            | API welcome message    |
| GET    | `/api/health`  | Health check           |
| GET    | `/docs`        | Swagger UI (auto-gen)  |
| GET    | `/redoc`       | ReDoc (auto-gen)       |

---

## License

MIT
