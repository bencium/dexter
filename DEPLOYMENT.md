# Dexter API Deployment Guide

Complete guide for deploying Dexter Financial Research API locally and to Fly.io.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [API Keys Setup](#api-keys-setup)
3. [Local Development](#local-development)
4. [Testing Locally](#testing-locally)
5. [Docker Testing](#docker-testing)
6. [Fly.io Deployment](#flyio-deployment)
7. [Post-Deployment](#post-deployment)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- **Python 3.10+**
- **uv** package manager: https://github.com/astral-sh/uv
- **Docker** (optional, for containerization): https://www.docker.com/get-started
- **Fly.io CLI** (for deployment): https://fly.io/docs/hands-on/install-flyctl/

### Install uv (if not installed)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Install Fly.io CLI
```bash
# macOS
brew install flyctl

# Linux
curl -L https://fly.io/install.sh | sh

# Windows
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

---

## API Keys Setup

### Required API Keys

#### 1. OpenAI API Key (Required)
- **Get it:** https://platform.openai.com/api-keys
- **Cost:** ~$10-30/month based on usage
- **Purpose:** Powers the AI agent

#### 2. Financial Data API Key (Choose One)

**Option A: Financial Datasets API** (Current Implementation)
- **Get it:** https://financialdatasets.ai
- **Cost:** $29-99/month (100 free calls/month)
- **Purpose:** Company financials, stock data

**Option B: yfinance (Recommended for MVP)** ⭐
- **Get it:** No API key needed!
- **Cost:** 100% FREE
- **Purpose:** Same financial data from Yahoo Finance
- **Note:** See [Alternative: Using yfinance](#alternative-using-yfinance) below

### Configure API Keys

1. **Copy environment template:**
```bash
cp env.example .env
```

2. **Edit `.env` file:**
```bash
# Required
OPENAI_API_KEY=sk-your-openai-key-here

# Choose one:
# Option A: Financial Datasets API
FINANCIAL_DATASETS_API_KEY=your-key-here

# Option B: yfinance (no key needed, modify code to use yfinance)
```

---

## Local Development

### 1. Install Dependencies
```bash
# Sync dependencies with uv
uv sync

# This installs:
# - FastAPI (web framework)
# - Uvicorn (ASGI server)
# - OpenAI client
# - LangChain
# - All other dependencies
```

### 2. Start API Server
```bash
# Method 1: Using uv
uv run dexter-api

# Method 2: Direct python
uv run python -m uvicorn dexter.api:app --reload --port 8000

# Server starts at: http://localhost:8000
```

### 3. Access API Documentation
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/api/health

---

## Testing Locally

### Run Automated Tests
```bash
# Start server in background
uv run python -m uvicorn dexter.api:app --host 0.0.0.0 --port 8000 > api_server.log 2>&1 &

# Run test suite
uv run python test_api.py

# Kill server when done
pkill -f "uvicorn dexter.api:app"
```

### Manual Testing with curl

**1. Check Health:**
```bash
curl http://localhost:8000/api/health
```

**2. Test Query Endpoint:**
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What was Apple'\''s revenue in the last quarter?"}'
```

**3. Check Status:**
```bash
curl http://localhost:8000/api/status
```

### Manual Testing with Python
```python
import requests

# Query endpoint
response = requests.post(
    "http://localhost:8000/api/query",
    json={"query": "What is Tesla's P/E ratio?"}
)
print(response.json())
```

---

## Docker Testing

Test your Docker build locally before deploying:

### 1. Build Docker Image
```bash
docker build -t dexter-api .
```

### 2. Run Container Locally
```bash
# Run with environment variables
docker run -p 8000:8000 \
  -e OPENAI_API_KEY="your-key" \
  -e FINANCIAL_DATASETS_API_KEY="your-key" \
  dexter-api

# Or use .env file
docker run -p 8000:8000 --env-file .env dexter-api
```

### 3. Test Docker Container
```bash
# In another terminal
curl http://localhost:8000/api/health
```

### 4. Stop Container
```bash
docker ps  # Get container ID
docker stop <container-id>
```

---

## Fly.io Deployment

### Step 1: Create Fly.io Account
```bash
# Sign up (if new user)
flyctl auth signup

# Or login (existing user)
flyctl auth login
```

### Step 2: Launch Application
```bash
# This will:
# - Create fly.toml (already exists)
# - Create Fly.io app
# - Configure resources
flyctl launch

# Answer prompts:
# - App name: dexter-api (or your choice)
# - Region: Choose closest to your users
# - Postgres: No (not needed for MVP)
# - Redis: No (not needed for MVP)
```

### Step 3: Set Environment Secrets
```bash
# Set OpenAI API key (REQUIRED)
flyctl secrets set OPENAI_API_KEY="sk-your-key-here"

# Set Financial Datasets API key (if using)
flyctl secrets set FINANCIAL_DATASETS_API_KEY="your-key-here"

# Verify secrets are set
flyctl secrets list
```

### Step 4: Deploy
```bash
# Deploy application
flyctl deploy

# This will:
# 1. Build Docker image
# 2. Push to Fly.io registry
# 3. Create VM instances
# 4. Start your API
```

### Step 5: Verify Deployment
```bash
# Get app URL
flyctl info

# Check app status
flyctl status

# View logs
flyctl logs

# Test health endpoint
curl https://dexter-api.fly.dev/api/health

# Test query endpoint
curl -X POST https://dexter-api.fly.dev/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Apple'\''s stock ticker?"}'
```

---

## Post-Deployment

### Monitor Your Application

**View Real-Time Logs:**
```bash
flyctl logs
```

**Check Metrics:**
```bash
# Open Fly.io dashboard
flyctl dashboard

# View in browser: https://fly.io/dashboard
```

**SSH into Container:**
```bash
flyctl ssh console
```

### Scale Your Application

**Increase Resources (if needed):**
```bash
# Scale to 512MB RAM (costs more)
flyctl scale memory 512

# Add more VMs
flyctl scale count 2

# Scale back to free tier
flyctl scale memory 256
flyctl scale count 1
```

**Auto-Scaling (already configured in fly.toml):**
- Automatically stops when idle
- Wakes up on request
- Scales to 0 machines when unused

### Update Deployment

**After code changes:**
```bash
# Deploy new version
flyctl deploy

# Rollback if issues
flyctl releases list
flyctl releases rollback <version>
```

### Cost Monitoring

**Check Usage:**
```bash
# View current month billing
flyctl dashboard

# Or visit: https://fly.io/dashboard/personal/billing
```

**Expected Costs (MVP):**
- **Free Tier:** $0/month (3 shared VMs, 256MB each)
- **Light Usage:** $0-10/month (with auto-sleep)
- **Growing:** $10-30/month (if staying awake 24/7)

---

## Troubleshooting

### Local Development Issues

**Problem: API won't start**
```bash
# Check if port 8000 is already in use
lsof -i :8000
kill -9 <PID>

# Try different port
uvicorn dexter.api:app --port 8001
```

**Problem: Missing dependencies**
```bash
# Reinstall dependencies
uv sync --reinstall
```

**Problem: API key not found**
```bash
# Verify .env file exists
cat .env

# Check keys are loaded
uv run python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('OPENAI_API_KEY'))"
```

### Docker Issues

**Problem: Build fails**
```bash
# Clear Docker cache
docker builder prune

# Rebuild without cache
docker build --no-cache -t dexter-api .
```

**Problem: Container crashes**
```bash
# View container logs
docker logs <container-id>

# Run interactive shell
docker run -it --entrypoint /bin/bash dexter-api
```

### Fly.io Issues

**Problem: Deployment fails**
```bash
# View detailed logs
flyctl logs

# Check secrets are set
flyctl secrets list

# Verify Dockerfile builds locally
docker build -t dexter-api .
```

**Problem: App is slow**
- **Cold starts:** First request after idle takes 1-3 seconds
- **Solution:** Keep at least 1 machine running (costs ~$3-5/month)
```bash
flyctl scale count 1 --min-machines-running=1
```

**Problem: Out of memory**
```bash
# Scale memory (costs more)
flyctl scale memory 512
```

**Problem: Can't reach API**
```bash
# Check app status
flyctl status

# Check SSL certificate
flyctl certs check

# Restart app
flyctl apps restart dexter-api
```

---

## Alternative: Using yfinance (100% Free)

Want to eliminate Financial Datasets API costs? Use yfinance:

### 1. Install yfinance
```bash
uv pip install yfinance
```

### 2. Modify Tools
Replace Financial Datasets API calls with yfinance:

```python
import yfinance as yf

def get_income_statements(ticker: str):
    stock = yf.Ticker(ticker)
    return stock.financials.to_dict()

def get_balance_sheets(ticker: str):
    stock = yf.Ticker(ticker)
    return stock.balance_sheet.to_dict()

def get_cash_flow(ticker: str):
    stock = yf.Ticker(ticker)
    return stock.cashflow.to_dict()
```

### 3. Update .env
```bash
# Only need OpenAI key
OPENAI_API_KEY=sk-your-key-here
# No FINANCIAL_DATASETS_API_KEY needed!
```

**Savings:** $29-99/month → $0/month

---

## Useful Commands

### Local Development
```bash
# Start API
uv run dexter-api

# Run tests
uv run python test_api.py

# Format code
uv run black src/

# Lint code
uv run pylint src/
```

### Docker
```bash
# Build
docker build -t dexter-api .

# Run
docker run -p 8000:8000 --env-file .env dexter-api

# Logs
docker logs <container-id>

# Shell
docker exec -it <container-id> /bin/bash
```

### Fly.io
```bash
# Deploy
flyctl deploy

# Logs
flyctl logs

# Status
flyctl status

# SSH
flyctl ssh console

# Restart
flyctl apps restart dexter-api

# Destroy (delete app)
flyctl apps destroy dexter-api
```

---

## Next Steps

1. **Local Testing:** ✅ Test API works locally
2. **Docker Testing:** Test containerization works
3. **Fly.io Deploy:** Deploy to production
4. **Add Features:**
   - Rate limiting
   - Authentication (JWT)
   - Caching (Redis)
   - Queue system (for long queries)
5. **Monitoring:**
   - Set up alerts (Fly.io dashboard)
   - Add error tracking (Sentry)
   - Monitor costs

---

## Support & Resources

- **Dexter GitHub:** https://github.com/virattt/dexter
- **Fly.io Docs:** https://fly.io/docs/
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **Fly.io Community:** https://community.fly.io/

---

**Deployment Status:**

| Component | Status | Notes |
|-----------|--------|-------|
| API Created | ✅ | FastAPI wrapper complete |
| Local Testing | ✅ | All tests passing |
| Docker | ✅ | Dockerfile ready |
| Fly.io Config | ✅ | fly.toml configured |
| Ready to Deploy | ✅ | Run `flyctl deploy` |

**Total Implementation Time:** ~4-6 hours
**Estimated Monthly Cost:** $10-40 (OpenAI + Fly.io)
**Monthly Cost (with yfinance):** $10-30 (OpenAI only)
