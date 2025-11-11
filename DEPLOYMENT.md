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

```bash
# Steps:
# 1. Create account at railway.app
# 2. Deploy from GitHub
# 3. Add services for Gradio and Slack bot
# 4. Set environment variables
# 5. Deploy!
```

### Option 3: Docker Container

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

### Start Bot
```bash
python slack_bot.py
# Keep running - uses Socket Mode (WebSocket)
```

---

## 🧪 Testing Your Deployment

### Test Gradio Dashboard
```bash
curl http://localhost:7860/
# Should return HTML
```

### Test Slack Bot
In Slack:
```
/mcp-monitor
# Should show help message

/mcp-monitor metrics
# Should show metrics
```

---

## 🔧 Troubleshooting

### Gradio Issues

**Port already in use:**
```bash
lsof -i :7860
kill -9 <PID>
```

**Module not found:**
```bash
pip install --upgrade -r requirements.txt
```

### Slack Bot Issues

**Not responding:**
- Check Socket Mode is enabled
- Verify bot token has `chat:write` scope
- Ensure slash command is created
- Check bot is invited to channel

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

---

## 📞 Support Resources

- **Gradio Docs**: https://gradio.app/docs
- **Slack API**: https://api.slack.com/docs
- **MCP Spec**: https://modelcontextprotocol.io
- **Hugging Face**: https://huggingface.co/docs

Good luck with your hackathon! 🚀
