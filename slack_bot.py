"""
Slack Bot Integration for MCP Monitoring
Handles slash commands and routes them to the Gradio interface
"""
import os
import asyncio
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from gradio_client import Client
import json

import config
from mcp_integration import mcp_integration

# Initialize Slack app
app = App(
    token=config.SLACK_BOT_TOKEN,
    signing_secret=config.SLACK_SIGNING_SECRET
)

# Gradio client (will connect to running Gradio app)
gradio_client = None
GRADIO_URL = None


def init_gradio_client(url: str):
    """Initialize connection to Gradio app"""
    global gradio_client, GRADIO_URL
    GRADIO_URL = url
    try:
        gradio_client = Client(url)
        print(f"✅ Connected to Gradio app at {url}")
    except Exception as e:
        print(f"⚠️  Could not connect to Gradio app: {e}")
        print("   Bot will operate in direct mode")


@app.command("/mcp-monitor")
def handle_mcp_monitor(ack, say, command):
    """
    Handle /mcp-monitor slash command
    
    Usage examples:
    - /mcp-monitor show session=session-001
    - /mcp-monitor metrics
    - /mcp-monitor context session=session-001
    - /mcp-monitor seen session=session-001
    """
    # Acknowledge command request immediately (within 3s)
    ack()
    
    query = command.get("text", "").strip()
    user_id = command.get("user_id")
    channel_id = command.get("channel_id")
    
    # If no query provided, show help
    if not query:
        say(
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": """*MCP Monitoring Interface* 🔍

Available commands:
• `/mcp-monitor show [session=SESSION_ID] [task=TASK_ID]` - Show logs
• `/mcp-monitor context session=SESSION_ID` - Display provided context
• `/mcp-monitor seen session=SESSION_ID` - Show agent-processed data
• `/mcp-monitor metrics [session=SESSION_ID]` - View performance metrics
• `/mcp-monitor link` - Get link to full dashboard

Try `/mcp-monitor metrics` to get started!"""
                    }
                }
            ]
        )
        return
    
    # Handle 'link' command specially
    if query.lower() == 'link':
        if GRADIO_URL:
            say(f"📊 Access the full monitoring dashboard: {GRADIO_URL}")
        else:
            say("⚠️ Dashboard URL not configured. Please set GRADIO_URL in your environment.")
        return
    
    # Process the query
    try:
        # Try using Gradio client if available
        if gradio_client:
            response = process_via_gradio(query)
        else:
            # Fallback to direct MCP integration
            response = process_directly(query)
        
        # Format response for Slack
        formatted_response = format_slack_response(response, query)
        
        say(
            blocks=formatted_response,
            text=f"MCP Monitor: {query}"  # Fallback text
        )
        
    except Exception as e:
        say(f"❌ Error processing command: {str(e)}\n\nPlease try again or use `/mcp-monitor link` to access the web interface.")


def process_via_gradio(query: str) -> dict:
    """Process query through Gradio interface"""
    try:
        # Call the Gradio endpoint
        result = gradio_client.predict(
            message=query,
            history=[],
            api_name="/chat"
        )
        
        return {
            'success': True,
            'message': result[0] if result else "No response",
            'data': result[1] if len(result) > 1 else None
        }
    except Exception as e:
        raise Exception(f"Gradio client error: {str(e)}")


def process_directly(query: str) -> dict:
    """Process query directly through MCP integration"""
    # Parse the query
    if query.startswith('metrics'):
        metrics = mcp_integration.get_monitoring_metrics()
        return {
            'success': True,
            'type': 'metrics',
            'data': metrics
        }
    
    elif query.startswith('show'):
        # Extract session/task if provided
        parts = query.split()
        session_id = None
        task_id = None
        
        for part in parts[1:]:
            if '=' in part:
                key, value = part.split('=', 1)
                if key == 'session':
                    session_id = value
                elif key == 'task':
                    task_id = value
        
        logs_df = mcp_integration.get_session_logs(
            session_id=session_id,
            task_id=task_id,
            limit=10
        )
        
        return {
            'success': True,
            'type': 'logs',
            'data': logs_df.to_dict('records') if not logs_df.empty else []
        }
    
    elif query.startswith('context'):
        # Extract session
        parts = query.split()
        session_id = 'session-001'  # Default
        
        for part in parts[1:]:
            if '=' in part:
                key, value = part.split('=', 1)
                if key == 'session':
                    session_id = value
        
        # Get context asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        context_data = loop.run_until_complete(
            mcp_integration.get_provided_context(session_id=session_id)
        )
        loop.close()
        
        return {
            'success': True,
            'type': 'context',
            'data': context_data
        }
    
    else:
        return {
            'success': False,
            'message': 'Unknown command. Use /mcp-monitor for help.'
        }


def format_slack_response(response: dict, query: str) -> list:
    """Format response as Slack blocks"""
    blocks = []
    
    if not response.get('success', False):
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"❌ {response.get('message', 'Error processing request')}"
            }
        })
        return blocks
    
    # Header
    blocks.append({
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": f"🔍 MCP Monitor: {query}",
            "emoji": True
        }
    })
    
    # Handle different response types
    response_type = response.get('type', 'message')
    
    if response_type == 'metrics':
        metrics = response.get('data', {})
        
        fields = []
        for key, value in metrics.items():
            fields.append({
                "type": "mrkdwn",
                "text": f"*{key.replace('_', ' ').title()}*\n{value}"
            })
        
        blocks.append({
            "type": "section",
            "fields": fields
        })
    
    elif response_type == 'logs':
        logs = response.get('data', [])
        
        if not logs:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "No logs found for this query."
                }
            })
        else:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Found *{len(logs)}* log entries (showing most recent):"
                }
            })
            
            for log in logs[:5]:  # Show max 5 in Slack
                log_text = f"• *{log.get('type', 'unknown')}* - {log.get('details', 'No details')}\n"
                log_text += f"  _Session: {log.get('session_id', 'N/A')}_"
                
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": log_text
                    }
                })
    
    elif response_type == 'context':
        context = response.get('data', {})
        
        context_text = "*Context Information:*\n"
        if 'files' in context:
            context_text += f"• Files: {len(context['files'])}\n"
        if 'commits' in context:
            context_text += f"• Commits: {len(context['commits'])}\n"
        if 'tokens' in context:
            context_text += f"• Tokens: {context['tokens']}\n"
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": context_text
            }
        })
    
    else:
        # Generic message response
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": response.get('message', 'Response received')
            }
        })
    
    # Add action button to view in dashboard
    if GRADIO_URL:
        blocks.append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "📊 View Full Dashboard",
                        "emoji": True
                    },
                    "url": GRADIO_URL,
                    "action_id": "view_dashboard"
                }
            ]
        })
    
    return blocks


@app.event("app_mention")
def handle_app_mention(event, say):
    """Handle when bot is mentioned"""
    text = event.get("text", "")
    
    # Remove bot mention and process as command
    query = text.split(maxsplit=1)[1] if len(text.split()) > 1 else ""
    
    if query:
        # Process similar to slash command
        try:
            if gradio_client:
                response = process_via_gradio(query)
            else:
                response = process_directly(query)
            
            formatted_response = format_slack_response(response, query)
            say(blocks=formatted_response)
        except Exception as e:
            say(f"❌ Error: {str(e)}")
    else:
        say("Hi! Use `/mcp-monitor` to interact with the monitoring interface.")


def start_bot(gradio_url: str = None):
    """Start the Slack bot"""
    if gradio_url:
        init_gradio_client(gradio_url)
    
    print("⚡️ Starting Slack bot...")
    
    # Use Socket Mode for local development
    if config.SLACK_APP_TOKEN:
        handler = SocketModeHandler(app, config.SLACK_APP_TOKEN)
        handler.start()
    else:
        # HTTP mode
        app.start(port=int(os.environ.get("PORT", 3000)))


if __name__ == "__main__":
    # Get Gradio URL from environment or use default
    gradio_url = os.getenv("GRADIO_URL", "http://localhost:7860")
    
    print("🤖 MCP Monitoring Slack Bot")
    print(f"Gradio Dashboard: {gradio_url}")
    print("\nStarting bot...")
    
    start_bot(gradio_url)
