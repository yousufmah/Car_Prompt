# CarPrompt 🚗

> Why search it, when you can prompt it?

AI-powered car search. Describe your perfect car in plain English — CarPrompt uses OpenAI to parse your intent and match you to the best listings.

---

## Stack

| Layer | Tech |
|---|---|
| Frontend | Next.js (TypeScript) + Tailwind CSS |
| Backend | Python + FastAPI |
| Database | PostgreSQL + pgvector |
| AI | OpenAI (gpt-4o-mini + text-embedding-ada-002) |
| Hosting | Vercel (frontend) + Railway (backend + DB) |
| Domain  | carprompt.co.uk |

---

## Production Deployment

Domain `carprompt.co.uk` acquired 2026‑02‑27. For detailed deployment instructions, see [DEPLOY.md](DEPLOY.md).

Quick steps:
1. Deploy frontend to Vercel, connect domain
2. Deploy backend + database to Railway
3. Set DNS records at registrar
4. Set up email forwarding (e.g., hello@carprompt.co.uk)

---

## Local Development

### Prerequisites
- [Docker](https://docker.com) (for the database)
- Python 3.11+
- Node.js 18+
- An OpenAI API key

---

### 1. Start the database

```bash
docker-compose up -d
```

This starts PostgreSQL with the pgvector extension on port 5432.

---

### 2. Set up the backend

```bash
cd backend
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Seed the database with mock listings:

```bash
python seed.py
```

Start the API:

```bash
uvicorn app.main:app --reload
```

API runs at `http://localhost:8000`  
Docs at `http://localhost:8000/docs`

---

### 3. Set up the frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:3000`

---

## How It Works

1. User types a natural language prompt: *"Reliable Japanese car under £8k, good on fuel"*
2. Backend sends it to GPT-4o-mini, which returns structured filters (make, price, fuel type, etc.)
3. Those filters query the database
4. If the prompt contains descriptive keywords, vector similarity search finds semantically relevant listings
5. Results are ranked and returned

---

## Project Structure

```
Car_Prompt/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app entry point
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── database.py      # DB connection
│   │   ├── ai.py            # OpenAI prompt parsing + embeddings
│   │   └── routes/
│   │       ├── search.py    # POST /api/search — core feature
│   │       ├── listings.py  # CRUD for car listings
│   │       └── garages.py   # CRUD for garages
│   ├── seed.py              # Mock data seeder
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   └── src/app/
│       ├── page.tsx         # Landing page
│       ├── search/page.tsx  # Search results
│       └── listing/[id]/    # Individual listing
├── docs/
│   └── PLAN.md              # Full product roadmap
├── docker-compose.yml       # PostgreSQL + pgvector
└── backend/tests/           # API tests (pytest)
```

---

## Roadmap

See [`docs/PLAN.md`](docs/PLAN.md) for the full roadmap.

**MVP (Phase 1):**
- [x] Landing page with prompt search bar
- [x] AI prompt parsing into structured filters
- [x] Search results page
- [x] Individual listing page
- [ ] Garage signup flow
- [ ] Mobile polish

**Phase 2:**
- [ ] User accounts (saved searches, favourites)
- [ ] Garage dashboard
- [ ] Price prediction ("good deal" badges)
- [ ] Conversational refinement

---

## Testing

API tests are available in the `backend/tests/` directory. To run tests:

```bash
cd backend
# Install test dependencies
pip install -r requirements-test.txt
# Run tests
pytest tests/ -v
```

See [`backend/tests/README.md`](backend/tests/README.md) for detailed test documentation.

## Contributing

This is a private project. Contact [@yousufmah](https://github.com/yousufmah) for access.
