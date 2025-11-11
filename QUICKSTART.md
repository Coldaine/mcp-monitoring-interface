# Quick Start Guide

Get the MCP Monitoring Interface running in under 5 minutes!

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (for cloning the repository)

## Installation

### Option 1: Using the Startup Script (Recommended)

**Windows:**
```bash
# Double-click start.bat or run:
start.bat
```

**Mac/Linux:**
```bash
chmod +x start.sh
./start.sh
```

The startup script will:
1. Activate your virtual environment (if available)
2. Run component tests
3. Launch the Gradio interface

### Option 2: Manual Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Tests** (Optional but Recommended)
   ```bash
   python test_app.py
   ```

3. **Start the Application**
   ```bash
   python gradio_app.py
   ```

## Accessing the Dashboard

Once started, open your browser and navigate to:
```
http://localhost:7860
```

You should see the MCP Monitoring Interface with three tabs:
- **Monitor Chat**: Interactive query interface
- **Metrics Dashboard**: Real-time performance metrics
- **Session Explorer**: Deep-dive into specific sessions

## Quick Commands to Try

In the Monitor Chat tab, try these commands:

```
/metrics
```
View overall performance metrics

```
/show session=session-001
```
Show logs for a specific session

```
/context session=session-001
```
Display context provided to the agent

```
/seen session=session-001
```
Show what the agent actually processed

## Sample Data

The application comes pre-loaded with sample data for testing. You'll see:
- 3 sample log entries
- Metrics from test sessions (session-001, session-002)
- Example context and seen data

## Configuration

Edit the `.env` file to customize:

```bash
# Change the port
GRADIO_SERVER_PORT=7860

# Enable sharing (creates public link)
GRADIO_SHARE=False

# Add authentication
ENABLE_AUTH=False
GRADIO_AUTH=username:password
```

## Optional: Slack Bot Integration

To enable Slack integration:

1. **Create a Slack App** at https://api.slack.com/apps
2. **Configure your tokens** in `.env`:
   ```bash
   SLACK_BOT_TOKEN=xoxb-your-token
   SLACK_APP_TOKEN=xapp-your-token
   SLACK_SIGNING_SECRET=your-secret
   ```

3. **Start the bot**:
   ```bash
   python slack_bot.py
   ```

4. **Use in Slack**:
   ```
   /mcp-monitor metrics
   /mcp-monitor show session=session-001
   ```

## Troubleshooting

### Port Already in Use
If port 7860 is occupied, change it in `.env`:
```bash
GRADIO_SERVER_PORT=7861
```

### Import Errors
Reinstall dependencies:
```bash
pip install -r requirements.txt --force-reinstall
```

### No Sample Data
Sample data is generated automatically on startup. If you don't see any:
```bash
python test_app.py
```

### Windows Encoding Issues
If you see Unicode errors, ensure your terminal supports UTF-8:
```bash
chcp 65001
```

## Next Steps

- **Connect to Real MCP Server**: Update `MCP_SERVER_URL` in `.env`
- **Customize Styling**: Edit `custom_styles.css`
- **Add More Features**: Extend `mcp_integration.py` with custom tools
- **Deploy**: See `DEPLOYMENT.md` for deployment options

## Need Help?

- Check the full [README.md](README.md) for detailed documentation
- Review [DEPLOYMENT.md](DEPLOYMENT.md) for production setup
- Run tests: `python test_app.py`

## Project Structure

```
mcp-monitoring-interface/
├── gradio_app.py          # Main Gradio application
├── slack_bot.py           # Slack bot integration
├── mcp_integration.py     # MCP server communication
├── utils.py               # Helper functions
├── config.py              # Configuration management
├── test_app.py            # Component tests
├── start.bat              # Windows startup script
├── start.sh               # Unix/Mac startup script
├── requirements.txt       # Python dependencies
├── custom_styles.css      # UI styling
├── .env                   # Configuration (created from .env.example)
└── README.md              # Full documentation
```

---

Built for the MCP Hackathon 2025
