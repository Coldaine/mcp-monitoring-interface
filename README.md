# MCP Monitoring Interface

A comprehensive Gradio-based monitoring dashboard for Model Context Protocol (MCP) interactions with Slack bot integration.

## 🚀 Features

- **Real-time Monitoring**: Track MCP server contexts, agent observations, and performance metrics
- **Slash Command Integration**: Control monitoring through Slack commands
- **Interactive Dashboard**: Gradio-powered UI with multiple tabs:
  - Monitor Chat: Interactive query interface
  - Metrics Dashboard: Real-time performance visualization  
  - Session Explorer: Deep-dive into specific sessions
- **Context Tracking**: Visualize what context is provided to agents vs. what they actually process
- **Performance Analytics**: Latency tracking, error rates, and token usage

## 📋 Prerequisites

- Python 3.8+
- Slack workspace (for bot integration)
- MCP server (or use the built-in mock for testing)

## 🔧 Installation

### 1. Clone and Setup

```bash
# Create project directory
mkdir mcp-monitoring-interface
cd mcp-monitoring-interface

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the project root:

```bash
# Slack Configuration
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
SLACK_SIGNING_SECRET=your-signing-secret

# Gradio Configuration
GRADIO_SERVER_PORT=7860
GRADIO_SERVER_NAME=0.0.0.0
GRADIO_SHARE=False
GRADIO_URL=http://localhost:7860

# MCP Server Configuration
MCP_SERVER_URL=http://localhost:8000
MCP_API_KEY=your-api-key-if-needed

# Monitoring Settings
LOG_RETENTION_DAYS=7
MAX_LOG_ENTRIES=1000
ENABLE_REAL_TIME_STREAMING=True

# Optional: Authentication
ENABLE_AUTH=False
GRADIO_AUTH=username:password
```

### 3. Slack App Setup (Optional but Recommended)

1. Go to [https://api.slack.com/apps](https://api.slack.com/apps)
2. Click "Create New App" → "From scratch"
3. Configure:
   - **OAuth & Permissions**: Add scopes:
     - `chat:write`
     - `commands`
     - `app_mentions:read`
   - **Slash Commands**: Create `/mcp-monitor` command
   - **Event Subscriptions**: Subscribe to `app_mention`
   - **Socket Mode**: Enable and generate App Token
4. Install app to workspace and copy tokens to `.env`

## 🎯 Usage

### Starting the Gradio Dashboard

```bash
python gradio_app.py
```

Access at: `http://localhost:7860`

### Starting the Slack Bot

```bash
python slack_bot.py
```

### Slash Command Examples

In Slack:
```
/mcp-monitor                               # Show help
/mcp-monitor metrics                       # View performance metrics
/mcp-monitor show session=session-001      # Show logs for session
/mcp-monitor context session=session-001   # Display provided context
/mcp-monitor seen session=session-001      # Show agent-processed data
/mcp-monitor link                          # Get dashboard URL
```

### Programmatic Usage

```python
from mcp_integration import mcp_integration

# Sample repository context
context = await mcp_integration.sample_repo_context(
    task="DevOps deployment optimization",
    repo_path="/path/to/repo",
    session_id="my-session"
)

# Get monitoring metrics
metrics = mcp_integration.get_monitoring_metrics(session_id="my-session")

# Retrieve session logs
logs = mcp_integration.get_session_logs(session_id="my-session", limit=50)
```

## 📊 Dashboard Features

### 1. Monitor Chat Tab
- Interactive chat interface for querying monitoring data
- Supports natural language and slash commands
- Real-time data display with formatted tables

### 2. Metrics Dashboard Tab
- Total requests counter
- Average latency tracking
- Error rate monitoring
- Context provisioning statistics
- Interactive latency visualization

### 3. Session Explorer Tab
- Deep-dive into specific sessions
- View all logs for a session
- Track context flow and agent observations

## 🏗️ Architecture

```
mcp-monitoring-interface/
├── gradio_app.py           # Main Gradio application
├── slack_bot.py            # Slack bot integration
├── mcp_integration.py      # MCP server communication layer
├── utils.py                # Helper functions and LogManager
├── config.py               # Configuration management
├── requirements.txt        # Python dependencies
├── static/
│   └── custom_styles.css   # Custom UI styles
└── .env                    # Environment variables
```

## 🔌 Integration with Your MCP Server

To connect to your actual MCP server, update `mcp_integration.py`:

```python
# Replace placeholder methods with actual API calls
async def get_provided_context(self, session_id: str, task_id: str = None):
    # Your actual implementation
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{self.server_url}/your-context-endpoint",
            params={"session_id": session_id}
        )
        return response.json()
```

## 🚢 Deployment

### Deploy Gradio to Hugging Face Spaces

```bash
# Install Hugging Face CLI
pip install huggingface_hub

# Login
huggingface-cli login

# Create Space and push
# Follow: https://huggingface.co/docs/hub/spaces-sdks-gradio
```

### Deploy Slack Bot to Render/Heroku

**Render:**
```bash
# Create render.yaml
services:
  - type: web
    name: mcp-slack-bot
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python slack_bot.py
```

**Heroku:**
```bash
heroku create mcp-monitoring-bot
git push heroku main
heroku config:set SLACK_BOT_TOKEN=your-token
```

## 🎨 Customization

### Modify Figma-Inspired Styles

Edit `static/custom_styles.css` to match your design system:

```css
:root {
    --primary-color: #your-brand-color;
    --secondary-color: #your-accent-color;
}
```

### Add Custom Metrics

In `mcp_integration.py`:

```python
def get_monitoring_metrics(self, session_id: str = None) -> Dict[str, Any]:
    metrics = self.log_manager.get_metrics(session_id)
    
    # Add custom metrics
    metrics['custom_metric'] = self.calculate_custom_metric()
    
    return metrics
```

## 🧪 Testing

```python
# Generate sample logs for testing
from utils import generate_sample_logs
from mcp_integration import mcp_integration

for log in generate_sample_logs():
    mcp_integration.log_manager.add_log(log)
```

## 📝 Hackathon Tips

For the November 14 sprint:

1. **Tag appropriately**: Emphasize "observability" and "developer tools"
2. **Demo video**: Show slash commands → Gradio dashboard flow
3. **Highlight uniqueness**: First slash-command-triggered MCP monitor
4. **Show metrics**: Token efficiency gains, context tracking benefits
5. **Include visuals**: Screenshots of Figma designs → actual UI

## 🤝 Contributing

This is a hackathon sprint project! Feel free to:
- Add new slash commands
- Enhance visualizations
- Improve MCP server integrations
- Add authentication layers

## 📄 License

MIT License - feel free to use for your hackathon projects!

## 🆘 Troubleshooting

**Gradio won't start:**
- Check port 7860 isn't in use: `lsof -i :7860`
- Verify all dependencies installed: `pip install -r requirements.txt`

**Slack bot not responding:**
- Verify tokens in `.env`
- Check Socket Mode is enabled in Slack app settings
- Ensure bot has necessary OAuth scopes

**No data showing:**
- Run with sample data: Uncomment `generate_sample_logs()` in `gradio_app.py`
- Check MCP_SERVER_URL is correct
- Verify MCP server is running

## 🔗 Resources

- [Gradio Documentation](https://gradio.app/docs/)
- [MCP Protocol Spec](https://modelcontextprotocol.io/)
- [Slack Bolt Python](https://slack.dev/bolt-python/)
- [Hugging Face Spaces](https://huggingface.co/docs/hub/spaces)

---

Built for the MCP Hackathon 2025 🚀
