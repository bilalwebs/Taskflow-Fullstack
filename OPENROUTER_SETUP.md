# OpenRouter Configuration Guide

## What Changed

The application has been configured to use **OpenRouter** instead of OpenAI directly.

### Files Modified:
1. `backend/src/config.py` - Added `OPENAI_BASE_URL` setting
2. `backend/src/agents/task_agent.py` - Updated to support custom base URL
3. `backend/src/services/agent_service.py` - Updated to support custom base URL
4. `backend/.env` - Added OpenRouter configuration

---

## Configuration in .env

```env
# OpenRouter Configuration
OPENAI_API_KEY=your-openrouter-api-key-here
OPENAI_MODEL=openai/gpt-4o-mini
OPENAI_BASE_URL=https://openrouter.ai/api/v1
```

### Important Notes:

1. **API Key**: Use your OpenRouter API key (starts with `sk-or-...`)
2. **Model Format**: OpenRouter uses format `provider/model-name`
3. **Base URL**: Must be `https://openrouter.ai/api/v1`

---

## Available Models on OpenRouter

You can use any model available on OpenRouter. Popular choices:

### OpenAI Models (via OpenRouter):
```env
OPENAI_MODEL=openai/gpt-4o-mini          # Fast and cheap
OPENAI_MODEL=openai/gpt-4o               # Most capable
OPENAI_MODEL=openai/gpt-3.5-turbo        # Cheapest
```

### Anthropic Models:
```env
OPENAI_MODEL=anthropic/claude-3.5-sonnet # Excellent reasoning
OPENAI_MODEL=anthropic/claude-3-haiku    # Fast and cheap
```

### Google Models:
```env
OPENAI_MODEL=google/gemini-pro           # Good balance
OPENAI_MODEL=google/gemini-flash-1.5     # Very fast
```

### Meta Models:
```env
OPENAI_MODEL=meta-llama/llama-3.1-70b-instruct  # Open source
```

### Free Models:
```env
OPENAI_MODEL=google/gemini-flash-1.5-8b  # Free tier
OPENAI_MODEL=meta-llama/llama-3.2-3b-instruct  # Free tier
```

---

## Getting Your OpenRouter API Key

1. Go to https://openrouter.ai/
2. Sign up or log in
3. Go to https://openrouter.ai/keys
4. Create a new API key
5. Copy the key (starts with `sk-or-...`)
6. Add credits to your account at https://openrouter.ai/credits

---

## Current Configuration

Your `.env` file is currently set to:

```env
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=openai/gpt-4o-mini
OPENAI_BASE_URL=https://openrouter.ai/api/v1
```

**⚠️ IMPORTANT**: Replace `your-api-key-here` with your actual API key. Use an OpenRouter key (starts with `sk-or-`) for OpenRouter, or an OpenAI key (starts with `sk-proj-`) for direct OpenAI access.

---

## What You Need to Do

### Option 1: Use OpenRouter (Recommended)
1. Get an OpenRouter API key from https://openrouter.ai/keys
2. Update your `.env` file:
   ```env
   OPENAI_API_KEY=sk-or-v1-YOUR-OPENROUTER-KEY-HERE
   OPENAI_MODEL=openai/gpt-4o-mini
   OPENAI_BASE_URL=https://openrouter.ai/api/v1
   ```
3. Add credits to your OpenRouter account
4. Restart backend

### Option 2: Use OpenAI Directly
1. Get credits on your OpenAI account
2. Update your `.env` file:
   ```env
   OPENAI_API_KEY=sk-proj-YOUR-OPENAI-KEY-HERE
   OPENAI_MODEL=gpt-4o-mini
   OPENAI_BASE_URL=
   ```
3. Restart backend

---

## Testing the Configuration

After updating your `.env` file and restarting the backend:

1. Go to http://localhost:3000/chat
2. Send a message: "hi"
3. Check backend logs for:
   - ✅ No 429 quota errors
   - ✅ Successful API response
   - ✅ Chat assistant responds

---

## Troubleshooting

### Error: 429 Insufficient Quota
- **Cause**: No credits on the account
- **Solution**: Add credits to OpenRouter or OpenAI account

### Error: 401 Unauthorized
- **Cause**: Invalid API key
- **Solution**: Check API key is correct and active

### Error: 404 Model Not Found
- **Cause**: Model name incorrect for OpenRouter
- **Solution**: Use format `provider/model-name` (e.g., `openai/gpt-4o-mini`)

### Error: Connection Failed
- **Cause**: Wrong base URL
- **Solution**: Use `https://openrouter.ai/api/v1` for OpenRouter

---

## Cost Comparison

OpenRouter often has better pricing than direct OpenAI:

| Model | OpenAI Direct | OpenRouter |
|-------|---------------|------------|
| GPT-4o-mini | $0.15/1M tokens | $0.15/1M tokens |
| GPT-4o | $2.50/1M tokens | $2.50/1M tokens |
| Claude 3.5 Sonnet | N/A | $3.00/1M tokens |
| Gemini Flash | N/A | Free tier available |

Plus OpenRouter gives you access to many more models!

---

## Next Steps

1. **Get the correct API key** (OpenRouter or OpenAI)
2. **Update `.env` file** with correct configuration
3. **Restart backend server**
4. **Test chat functionality**

Let me know which option you choose and I'll help you configure it!
