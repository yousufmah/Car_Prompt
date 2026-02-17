# Car Prompt — Project Plan

## Vision
AI-powered car search platform. Users describe what they want in plain English, get matched to the best listings. Undercut AutoTrader with fair pricing for garages.

## MVP Features (Phase 1)
- [ ] Landing page with prompt search bar
- [ ] User types a prompt → LLM parses into structured filters
- [ ] Database of car listings (seeded manually / from garages)
- [ ] Results page with ranked matches
- [ ] Individual car listing page
- [ ] Basic garage signup (add listings)
- [ ] Mobile responsive

## Phase 2
- [ ] User accounts (save searches, favourites)
- [ ] Garage dashboard (manage listings, view analytics)
- [ ] Price prediction model ("good deal" badges)
- [ ] Conversational refinement ("show me something similar but newer")
- [ ] Email alerts for saved searches

## Phase 3
- [ ] Collaborative filtering recommendations
- [ ] Image-based search
- [ ] Review/rating system
- [ ] Payment integration (garage subscription / flat %)
- [ ] SEO optimisation for car searches

## Tech Stack
- **Frontend:** Next.js (TypeScript), Tailwind CSS
- **Backend:** Python (FastAPI)
- **Database:** PostgreSQL + pgvector
- **AI:** OpenAI API (prompt parsing + semantic search)
- **Hosting:** Vercel (frontend) + Railway (backend + DB)

## Data Model (Core)

### Car Listing
- id, title, description
- make, model, variant, year
- price, mileage
- fuel_type, transmission, body_type, doors
- colour, engine_size
- location (postcode/city)
- images (URLs)
- garage_id
- created_at, updated_at
- embedding (vector — for semantic search)

### Garage
- id, name, email, phone
- address, postcode
- subscription_tier
- created_at

### Search Log
- id, user_prompt, parsed_filters, results_count
- created_at
- (this data is GOLD for improving the model later)

## Name Decision
TBD — "Car Prompt" or "Prompt Car" — need to check domain availability
