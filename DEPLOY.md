# Deployment Guide – CarPrompt

This guide covers deploying CarPrompt to production with Vercel (frontend) and Railway (backend + database).

## Prerequisites

- GitHub repository: https://github.com/yousufmah/Car_Prompt
- Domain: carprompt.co.uk (purchased 2026-02-27)
- Accounts on [Vercel](https://vercel.com) and [Railway](https://railway.com)

## 1. Frontend – Vercel

### Automatic Deploy (Recommended)
1. Connect your GitHub repo to Vercel
2. Select the `frontend` directory as root
3. Add environment variable:
   - `NEXT_PUBLIC_API_URL`: https://carprompt-backend.up.railway.app
4. Deploy

### Manual Deploy
```bash
cd frontend
npm install
npx vercel --prod --token $VERCEL_TOKEN
```

### Custom Domain
In Vercel project settings > Domains, add `carprompt.co.uk` and `www.carprompt.co.uk`. Follow DNS instructions.

## 2. Backend – Railway

### Create New Service
1. Create a new Railway project
2. Link GitHub repo, select `backend` directory
3. Railway will detect `railway.json` and deploy automatically

### Environment Variables
Set the following in Railway dashboard:
- `DATABASE_URL`: PostgreSQL connection string (auto‑provisioned)
- `OPENAI_API_KEY`: Your OpenAI‑compatible API key (DeepSeek recommended)
  - If you don't have a key yet, set `OPENAI_API_KEY=mock` — filter‑based search will work, semantic search disabled
- `OPENAI_API_BASE`: https://api.deepseek.com (if using DeepSeek)

### Database
Railway automatically creates a PostgreSQL database. The app uses `pgvector` extension; ensure it's enabled.

### Health Check
The service includes a `/health` endpoint for monitoring.

## 3. DNS Configuration

### At Your Registrar
Add the following records (replace with actual Vercel targets):

| Type  | Name                | Value                          |
|-------|---------------------|--------------------------------|
| CNAME | carprompt.co.uk     | cname.vercel-dns.com           |
| CNAME | www.carprompt.co.uk | cname.vercel-dns.com           |

Wait up to 48 hours for propagation.

## 4. Email Forwarding

Most registrars offer free email forwarding. Set up forwarding for:

- hello@carprompt.co.uk → your personal email
- contact@carprompt.co.uk → your personal email

## 5. Post‑Deployment

1. Seed the database with mock listings:
   ```bash
   cd backend
   python seed.py
   ```
   (Requires database connection; adjust `DATABASE_URL` accordingly.)

2. Verify the API is reachable:
   ```
   https://carprompt-backend.up.railway.app/health
   ```

3. Test the frontend:
   ```
   https://carprompt.co.uk
   ```

## 6. Monitoring & Updates

- Vercel provides automatic SSL certificates
- Railway includes logging and metrics
- Consider setting up cron jobs for data updates (e.g., sync with Marketcheck API)

## Troubleshooting

- **Frontend not connecting to backend**: Check `NEXT_PUBLIC_API_URL` matches the deployed backend URL.
- **Database errors**: Ensure `pgvector` extension is installed (`CREATE EXTENSION vector;`).
- **Missing OpenAI key**: Use a mock key for development; for production, sign up for DeepSeek (cheaper) or OpenAI.

---

**Last Updated:** 2026‑02‑27  
**Maintainer:** Jarvis (AI assistant)