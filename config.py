"""
Configuration settings for MCP Monitoring Interface
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Slack Configuration
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "xoxb-your-bot-token")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN", "xapp-your-app-token")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET", "your-signing-secret")

# Gradio Configuration
GRADIO_SERVER_PORT = int(os.getenv("GRADIO_SERVER_PORT", "7860"))
GRADIO_SERVER_NAME = os.getenv("GRADIO_SERVER_NAME", "0.0.0.0")
GRADIO_SHARE = os.getenv("GRADIO_SHARE", "False").lower() == "true"
GRADIO_AUTH = os.getenv("GRADIO_AUTH", None)  # Format: "username:password"

# MCP Server Configuration
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
MCP_API_KEY = os.getenv("MCP_API_KEY", None)

# Monitoring Settings
LOG_RETENTION_DAYS = int(os.getenv("LOG_RETENTION_DAYS", "7"))
MAX_LOG_ENTRIES = int(os.getenv("MAX_LOG_ENTRIES", "1000"))
ENABLE_REAL_TIME_STREAMING = os.getenv("ENABLE_REAL_TIME_STREAMING", "True").lower() == "true"

# UI Customization
THEME = os.getenv("THEME", "default")  # Options: default, soft, monochrome, or custom
CUSTOM_CSS_PATH = os.getenv("CUSTOM_CSS_PATH", "static/custom_styles.css")

# Database Configuration (Optional)
DATABASE_URL = os.getenv("DATABASE_URL", None)

# Security
ENABLE_AUTH = os.getenv("ENABLE_AUTH", "False").lower() == "true"
ALLOWED_USERS = os.getenv("ALLOWED_USERS", "").split(",") if os.getenv("ALLOWED_USERS") else []
