# Dexter API - Quick Start Guide

## ⚡ Test Locally (5 minutes)

### 1. Setup API Keys
```bash
# Copy environment template
cp env.example .env

# Edit .env and add your keys
# OPENAI_API_KEY=sk-...
# FINANCIAL_DATASETS_API_KEY=...
```

### 2. Install & Run
```bash
# Install dependencies
uv sync

# Start API server
uv run dexter-api
```

### 3. Test It Works
```bash
# In another terminal, run tests
uv run python test_api.py
```

**API is now running at:** http://localhost:8000
**API Docs:** http://localhost:8000/docs

---

## 🚀 Deploy to Fly.io (10 minutes)

### 1. Install Fly.io CLI
```bash
# macOS
brew install flyctl

# Linux/Windows - see DEPLOYMENT.md
```

### 2. Login & Deploy
```bash
# Login to Fly.io
flyctl auth login

# Launch app (first time only)
flyctl launch

# Set API keys as secrets
flyctl secrets set OPENAI_API_KEY="sk-your-key"
flyctl secrets set FINANCIAL_DATASETS_API_KEY="your-key"

# Deploy!
flyctl deploy
```

### 3. Test Production
```bash
# Check it's live
flyctl status

# Test health
curl https://your-app.fly.dev/api/health

# View logs
flyctl logs
```

**Done! Your API is live** 🎉

---

## 💰 Cost Breakdown

### Current Setup (Financial Datasets API)
- OpenAI API: $10-30/month
- Financial Datasets: $29-99/month
- Fly.io: $0-10/month (free tier + auto-sleep)
- **Total: $40-140/month**

### Recommended Setup (yfinance - FREE)
- OpenAI API: $10-30/month
- yfinance: $0 (100% FREE)
- Fly.io: $0-10/month
- **Total: $10-40/month** ⭐

---

## 🔑 API Keys - Where to Get Them

### Required: OpenAI API Key
1. Go to: https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy key (starts with `sk-`)
4. Cost: ~$10-30/month

### Choose One Financial Data Provider:

**Option A: Financial Datasets (Current)**
- Get key: https://financialdatasets.ai
- Cost: $29-99/month
- Free tier: 100 calls/month

**Option B: yfinance (Recommended for MVP)** ⭐
- No API key needed!
- 100% FREE forever
- Same data quality
- See DEPLOYMENT.md for setup

### Free Alternatives Comparison

| Provider | Free Tier | Paid | API Key | Data Quality |
|----------|-----------|------|---------|--------------|
| **yfinance** | Unlimited | FREE | No | ⭐⭐⭐⭐⭐ |
| Alpha Vantage | 25/day | $50/mo | Yes | ⭐⭐⭐⭐ |
| IEX Cloud | 50K/mo | $9/mo | Yes | ⭐⭐⭐⭐ |
| Financial Datasets | 100/mo | $29/mo | Yes | ⭐⭐⭐⭐⭐ |

---

## 📝 Key Files Created

```
dexter/
├── src/dexter/api.py          # ✅ FastAPI application
├── test_api.py                # ✅ Test suite
├── Dockerfile                 # ✅ Container config
├── fly.toml                   # ✅ Fly.io config
├── requirements.txt           # ✅ Dependencies
├── DEPLOYMENT.md              # ✅ Full deployment guide
└── QUICK_START.md            # ✅ This file
```

---

## 🧪 Test Commands

### Local Testing
```bash
# Start server
uv run dexter-api

# Run full test suite
uv run python test_api.py

# Manual test with curl
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Apple stock ticker?"}'
```

### Production Testing
```bash
# Check health
curl https://your-app.fly.dev/api/health

# Test query
curl -X POST https://your-app.fly.dev/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What was Tesla revenue last quarter?"}'
```

---

## 🆘 Quick Troubleshooting

### API won't start locally
```bash
# Check port 8000 is free
lsof -i :8000

# Reinstall dependencies
uv sync --reinstall
```

### Fly.io deployment fails
```bash
# View logs
flyctl logs

# Check secrets
flyctl secrets list

# Redeploy
flyctl deploy
```

### API keys not working
```bash
# Verify .env file
cat .env

# Check keys loaded
uv run python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('OpenAI:', bool(os.getenv('OPENAI_API_KEY')))"
```

---

## 🎯 Next Steps

1. ✅ **Local Testing Complete** - API works locally
2. ⏳ **Deploy to Fly.io** - Run `flyctl deploy`
3. ⏳ **Switch to yfinance** - Save $29-99/month (optional)
4. ⏳ **Add Features:**
   - Rate limiting
   - Authentication
   - Caching
   - Analytics

---

## 📚 Documentation

- **Full Deployment Guide:** `DEPLOYMENT.md`
- **API Documentation:** http://localhost:8000/docs (when running)
- **Fly.io Docs:** https://fly.io/docs/

---

## 💡 Pro Tips

1. **Use yfinance for MVP** - Save $29-99/month
2. **Let Fly.io auto-sleep** - Save money when not in use
3. **Monitor costs** - Check Fly.io dashboard weekly
4. **Start small** - Scale only when needed

---

**Status: ✅ Ready to Deploy!**

Run `flyctl deploy` to go live in 5 minutes.
