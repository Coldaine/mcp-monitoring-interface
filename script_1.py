
# Create a comprehensive deployment guide and quick start script

deployment_guide = """
# Quick Start & Deployment Guide

## 🚀 Fast Track Setup (5 minutes)

### Step 1: Install Dependencies
```bash
pip install gradio pandas plotly slack-bolt python-dotenv httpx
```

### Step 2: Set Environment Variables
```bash
# Minimal setup - just for testing Gradio interface
export GRADIO_SERVER_PORT=7860
export MCP_SERVER_URL=http://localhost:8000
```

### Step 3: Launch Dashboard
```bash
python gradio_app.py
```

Visit: http://localhost:7860

That's it! You now have a working monitoring dashboard with sample data.

---

## 📦 Production Deployment

### Option 1: Hugging Face Spaces (Recommended for Gradio)

#### Why Hugging Face?
- Free hosting for Gradio apps
- Automatic HTTPS
- Built-in monitoring
- Easy sharing

#### Steps:
1. Create account at https://huggingface.co
2. Create new Space:
   - SDK: Gradio
   - Hardware: CPU Basic (free)
3. Upload files:
   - gradio_app.py
   - mcp_integration.py
   - utils.py
   - config.py
   - requirements.txt
   - static/custom_styles.css
4. Set secrets in Space settings:
   - MCP_SERVER_URL
   - MCP_API_KEY (if needed)
5. Space will auto-deploy!

Your URL: https://huggingface.co/spaces/YOUR_USERNAME/mcp-monitoring

### Option 2: Railway (Full Stack)

#### Why Railway?
- Deploy both Gradio and Slack bot
- PostgreSQL database included
- Environment variable management
- GitHub integration

#### Steps:
1. Create account at https://railway.app
2. New Project → Deploy from GitHub
3. Add services:
   - **Gradio Service**: Start command: `python gradio_app.py`
   - **Slack Bot Service**: Start command: `python slack_bot.py`
4. Add PostgreSQL database (optional)
5. Set environment variables from .env.example
6. Deploy!

### Option 3: Render (Slack Bot + Gradio)

```yaml
# render.yaml
services:
  - type: web
    name: mcp-gradio-dashboard
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python gradio_app.py
    envVars:
      - key: GRADIO_SERVER_NAME
        value: 0.0.0.0
      - key: PORT
        value: 10000

  - type: web
    name: mcp-slack-bot
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python slack_bot.py
    envVars:
      - key: SLACK_BOT_TOKEN
        sync: false
      - key: SLACK_APP_TOKEN
        sync: false
```

### Option 4: Docker Container

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7860

CMD ["python", "gradio_app.py"]
```

```bash
# Build and run
docker build -t mcp-monitoring .
docker run -p 7860:7860 --env-file .env mcp-monitoring
```

---

## 🤖 Slack Bot Deployment

### Prerequisites
1. Create Slack App at https://api.slack.com/apps
2. Enable Socket Mode
3. Add OAuth Scopes: `chat:write`, `commands`, `app_mentions:read`
4. Create slash command: `/mcp-monitor`
5. Install app to workspace

### Environment Setup
```bash
SLACK_BOT_TOKEN=xoxb-...        # From OAuth & Permissions
SLACK_APP_TOKEN=xapp-...        # From Socket Mode
SLACK_SIGNING_SECRET=...        # From Basic Information
GRADIO_URL=https://your-gradio-url.com
```

### Deployment Options

#### A. Local Development
```bash
python slack_bot.py
# Keep running - uses Socket Mode (WebSocket)
```

#### B. Production Server
```bash
# Use process manager
pm2 start slack_bot.py --interpreter python3 --name mcp-slack-bot

# Or with systemd
sudo nano /etc/systemd/system/mcp-slack-bot.service
```

Systemd service file:
```ini
[Unit]
Description=MCP Monitoring Slack Bot
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/mcp-monitoring-interface
Environment="PATH=/path/to/venv/bin"
EnvironmentFile=/path/to/.env
ExecStart=/path/to/venv/bin/python slack_bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 🧪 Testing Your Deployment

### 1. Test Gradio Dashboard
```bash
curl http://localhost:7860/
# Should return HTML
```

### 2. Test MCP Integration
```python
from mcp_integration import mcp_integration
import asyncio

async def test():
    # Test sampling
    context = await mcp_integration.sample_repo_context(
        task="test task",
        session_id="test-session"
    )
    print(f"Context: {context}")
    
    # Test metrics
    metrics = mcp_integration.get_monitoring_metrics()
    print(f"Metrics: {metrics}")

asyncio.run(test())
```

### 3. Test Slack Bot
In Slack:
```
/mcp-monitor
# Should show help message

/mcp-monitor metrics
# Should show metrics
```

---

## 📊 Monitoring Your Monitor

### Health Checks

```python
# Add to gradio_app.py for health endpoint
@demo.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
```

### Uptime Monitoring
- Use UptimeRobot (free)
- Ping: https://your-app-url.com/health
- Alert on downtime

### Logs
```bash
# View Gradio logs
tail -f gradio_app.log

# View Slack bot logs  
tail -f slack_bot.log
```

---

## 🔧 Troubleshooting

### Gradio Issues

**Port already in use:**
```bash
# Find process
lsof -i :7860
# Kill it
kill -9 <PID>
```

**Module not found:**
```bash
pip install --upgrade -r requirements.txt
```

### Slack Bot Issues

**Not responding to commands:**
- Check Socket Mode is enabled
- Verify bot token has `chat:write` scope
- Ensure slash command URL is correct
- Check bot is invited to channel

**Connection errors:**
```bash
# Test bot token
curl -H "Authorization: Bearer $SLACK_BOT_TOKEN" https://slack.com/api/auth.test
```

### MCP Integration Issues

**Can't connect to MCP server:**
- Verify MCP_SERVER_URL is correct
- Check server is running: `curl $MCP_SERVER_URL/health`
- Check firewall rules

---

## 🎯 Hackathon Deployment Checklist

- [ ] Gradio app running on public URL
- [ ] Slack bot responding to commands
- [ ] Sample data loaded for demo
- [ ] Custom styling applied (Figma design)
- [ ] README with screenshots
- [ ] Demo video recorded
- [ ] GitHub repo published
- [ ] Hugging Face Space live
- [ ] Slack workspace invite ready
- [ ] Presentation slides prepared

---

## 📈 Performance Optimization

### For High Traffic

1. **Add Redis for caching:**
```python
import redis
cache = redis.Redis(host='localhost', port=6379)

def get_cached_metrics(session_id):
    key = f"metrics:{session_id}"
    cached = cache.get(key)
    if cached:
        return json.loads(cached)
    
    metrics = calculate_metrics(session_id)
    cache.setex(key, 300, json.dumps(metrics))  # 5min cache
    return metrics
```

2. **Use database for logs:**
```python
# In config.py
DATABASE_URL = "postgresql://user:pass@host/db"

# In utils.py  
from sqlalchemy import create_engine
engine = create_engine(DATABASE_URL)
```

3. **Enable Gradio queue:**
```python
demo.queue(concurrency_count=10)
demo.launch()
```

---

## 🔐 Security Hardening

### 1. Enable Authentication
```python
# In .env
ENABLE_AUTH=True
GRADIO_AUTH=admin:strong_password_here
```

### 2. Add Rate Limiting
```python
from slowapi import Limiter
limiter = Limiter(key_func=lambda: request.remote_addr)

@limiter.limit("10/minute")
def monitor_query(message, history):
    # Your code
```

### 3. Encrypt Secrets
```bash
# Use environment-specific secrets
# Never commit .env file
echo ".env" >> .gitignore
```

---

## 🚢 CI/CD Pipeline

### GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy to Hugging Face

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Push to HF Space
        env:
          HF_TOKEN: ${{ secrets.HF_TOKEN }}
        run: |
          git remote add hf https://huggingface.co/spaces/USER/SPACE
          git push hf main
```

---

## 📞 Support Resources

- **Gradio Docs**: https://gradio.app/docs
- **Slack API**: https://api.slack.com/docs
- **MCP Spec**: https://modelcontextprotocol.io
- **Hugging Face**: https://huggingface.co/docs

---

Good luck with your hackathon! 🚀
"""

print(deployment_guide)
print("\n" + "="*80)
print("DEPLOYMENT GUIDE CREATED")
print("="*80)
