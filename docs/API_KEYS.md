# API Keys Required for CarPrompt

For the AI features (prompt parsing and semantic search) you need an **OpenAI‑compatible API key**.

## Option 1: DeepSeek (Recommended)
- Cheaper than OpenAI, same API format
- Sign up at https://platform.deepseek.com/api
- Generate an API key
- Base URL: `https://api.deepseek.com`
- Models: `deepseek-chat` (for parsing), `deepseek-embed` (for embeddings)
- Cost: ~$0.14 per million tokens

## Option 2: OpenAI
- Sign up at https://platform.openai.com/api-keys
- Generate an API key
- Base URL: `https://api.openai.com/v1` (default)
- Models: `gpt-4o-mini` (parsing), `text-embedding-ada-002` (embeddings)
- Cost: ~$0.15 per million tokens (embedding) + $0.60 per million tokens (GPT)

## Environment Variables to Set

In Railway dashboard, add:

```bash
OPENAI_API_KEY=sk-xxxxxxxxxxxx
OPENAI_API_BASE=https://api.deepseek.com  # only if using DeepSeek
```

## Option 3: Mock Mode (No AI)
If you want to skip AI features for now, set:

```bash
OPENAI_API_KEY=mock
```

The backend will return empty filters and zero vectors — filter‑based search will still work, but semantic matching will be disabled.

---

**Recommendation:** Use DeepSeek. It's cheaper and works with the existing code (just change the base URL).