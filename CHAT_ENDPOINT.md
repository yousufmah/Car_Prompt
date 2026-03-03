# CarPrompt Conversational Chat Endpoint

## Overview

The new `/api/chat/` endpoint enables multi‑turn conversational car search. Instead of a single prompt, the system engages in a natural dialogue to gather missing details (budget, make, urgency, etc.) before returning matching cars.

## Endpoint

`POST /api/chat/`

## Request Body

```json
{
  "messages": [
    {"role": "user", "content": "I want a family car that fits 6 people comfortably"}
  ],
  "session_id": "optional-string"
}
```

- `messages`: Array of message objects in chronological order. Each object must have `role` (`"user"` or `"assistant"`) and `content` (string).
- `session_id`: Optional identifier for tracking conversations across requests (currently not used for state).

## Response

Two possible response types:

### 1. Clarification Needed (`type: "response"`)

```json
{
  "type": "response",
  "assistant_message": "Sure, I can help you find a great car! Could you tell me your budget range?",
  "filters": null,
  "results": null,
  "count": null
}
```

The client should display `assistant_message` and wait for the user's reply, then send a new request with the extended conversation history.

### 2. Search Results (`type: "search"`)

```json
{
  "type": "search",
  "assistant_message": "Here are some cars that match your criteria:",
  "filters": {
    "makes": [],
    "models": [],
    "min_year": null,
    "max_year": null,
    "min_price": null,
    "max_price": 20000,
    "max_mileage": null,
    "fuel_types": [],
    "transmissions": [],
    "body_types": [],
    "min_doors": null,
    "keywords": [],
    "sort_by": "relevance",
    "priority_factors": [],
    "use_case": []
  },
  "results": [
    {
      "id": 1,
      "title": "2020 Toyota Sienna",
      "make": "toyota",
      "model": "sienna",
      "year": 2020,
      "price": 18500,
      "mileage": 32000,
      "fuel_type": "petrol",
      "transmission": "automatic",
      "body_type": "mpv",
      "location": "London",
      "images": "https://example.com/image.jpg"
    }
  ],
  "count": 1
}
```

When `type` is `"search"`, the assistant has determined enough information is available and returns structured filters together with matching car listings. The frontend can display the results and optionally show the extracted filters.

## Conversation Example

**Request 1**
```json
{
  "messages": [
    {"role": "user", "content": "I want a family car that fits 6 people comfortably"}
  ]
}
```

**Response 1**
```json
{
  "type": "response",
  "assistant_message": "Sure, do you have a specific make in mind? How urgently do you need it? And what's the budget we're working with?"
}
```

**Request 2** (client adds user reply)
```json
{
  "messages": [
    {"role": "user", "content": "I want a family car that fits 6 people comfortably"},
    {"role": "assistant", "content": "Sure, do you have a specific make in mind? How urgently do you need it? And what's the budget we're working with?"},
    {"role": "user", "content": "No specific make, need it within a month, budget around £25,000"}
  ]
}
```

**Response 2** (may be `"search"` or further questions)
```json
{
  "type": "search",
  ...
}
```

## Implementation Notes

- The AI logic is in `app/ai.py` (function `chat_car_search`). It uses the same OpenAI client as the existing parser, falling back to mock mode when `OPENAI_API_KEY=mock`.
- The endpoint reuses the existing search infrastructure (filter building, vector search, logging).
- The conversation is stateless; the client must send the full message history each time.
- The system prompt encourages the assistant to ask about budget, make, urgency, vehicle type, fuel, transmission, year/mileage, doors/seats, and use case.

## Integration with Frontend

1. Replace the existing single‑prompt search box with a chat interface.
2. Maintain an array of messages locally (or in session storage).
3. On each user message, send the whole array to `/api/chat/`.
4. If response is `type: "response"`, append the assistant's message and wait for user input.
5. If response is `type: "search"`, display the cars and optionally the extracted filters.

## Testing with Mock Mode

If `OPENAI_API_KEY` is set to `"mock"`, the chat AI will simulate a simple two‑turn conversation:
1. First user message → asks about budget.
2. Any second user message → returns dummy filters (max_price 15000).

This allows development without an OpenAI key.

## Quick Test with curl

Start the backend locally (`uvicorn app.main:app --reload`), then:

```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "I want a family car that fits 6 people comfortably"}
    ]
  }'
```

You'll receive a response like:

```json
{
  "type": "response",
  "assistant_message": "Sure, do you have a specific make in mind? How urgently do you need it? And what's the budget we're working with?",
  "filters": null,
  "results": null,
  "count": null
}
```