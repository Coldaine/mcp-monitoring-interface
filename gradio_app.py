"""
Gradio Monitoring Interface Application
Main application for MCP monitoring with slash-command integration
"""
import gradio as gr
import pandas as pd
import asyncio
from datetime import datetime
from typing import List, Tuple, Dict, Any
import os

import config
from mcp_integration import mcp_integration
from utils import (
    format_context_for_display,
    format_seen_data_for_display,
    parse_slash_command,
    generate_sample_logs
)

# Custom CSS for enhanced styling (Figma-inspired)
CUSTOM_CSS = """
.container {
    max-width: 1400px;
    margin: auto;
}

.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 10px;
    margin: 10px 0;
}

.log-entry {
    border-left: 3px solid #667eea;
    padding-left: 15px;
    margin: 10px 0;
}

.context-display {
    background: #f7fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 15px;
    font-family: 'Monaco', monospace;
}

.chat-message {
    animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.header-title {
    background: linear-gradient(90deg, #667eea, #764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.5em;
    font-weight: bold;
    text-align: center;
    margin: 20px 0;
}
"""

# Load custom CSS if available
if os.path.exists(config.CUSTOM_CSS_PATH):
    with open(config.CUSTOM_CSS_PATH, 'r') as f:
        CUSTOM_CSS += f.read()


# Initialize with sample data for demonstration
for log in generate_sample_logs():
    mcp_integration.log_manager.add_log(log)


async def monitor_query(message: str, history: List) -> Tuple[str, pd.DataFrame]:
    """
    Main query handler for monitoring interface
    Processes slash commands and natural language queries
    """
    # Parse command if it starts with /
    if message.startswith('/'):
        command = message[1:]  # Remove leading /
        parsed = parse_slash_command(command)
        
        action = parsed['action']
        target = parsed['target']
        filters = parsed['filters']
        
        # Handle different commands
        if action == 'show' or action == 'context':
            session_id = filters.get('session')
            task_id = filters.get('task')
            
            if action == 'context':
                # Get context data
                context_data = await mcp_integration.get_provided_context(
                    session_id=session_id or 'session-001',
                    task_id=task_id
                )
                response = f"### Context Data\n\n{format_context_for_display(context_data)}"
                df = pd.DataFrame([context_data]) if context_data else pd.DataFrame()
            else:
                # Show general logs
                logs_df = mcp_integration.get_session_logs(
                    session_id=session_id,
                    task_id=task_id,
                    limit=20
                )
                response = f"### Logs Retrieved\n\nFound {len(logs_df)} log entries"
                df = logs_df
        
        elif action == 'seen':
            session_id = filters.get('session', 'session-001')
            seen_data = await mcp_integration.get_agent_seen_data(session_id)
            response = f"### Agent Seen Data\n\n{format_seen_data_for_display(seen_data)}"
            df = pd.DataFrame(seen_data) if seen_data else pd.DataFrame()
        
        elif action == 'metrics':
            session_id = filters.get('session')
            metrics = mcp_integration.get_monitoring_metrics(session_id=session_id)
            response = "### Performance Metrics\n\n"
            for key, value in metrics.items():
                response += f"**{key.replace('_', ' ').title()}:** {value}\n\n"
            df = pd.DataFrame([metrics]).T.reset_index()
            df.columns = ['Metric', 'Value']
        
        else:
            response = f"Unknown command: {action}\n\nAvailable commands: /show, /context, /seen, /metrics"
            df = pd.DataFrame()
    
    else:
        # Natural language query - show general overview
        response = """
### MCP Monitoring Dashboard

Welcome to the MCP Monitoring Interface! Here's what you can do:

**Available Commands:**
- `/show [session=SESSION_ID] [task=TASK_ID]` - Show logs
- `/context session=SESSION_ID` - Display provided context
- `/seen session=SESSION_ID` - Show agent-processed data  
- `/metrics [session=SESSION_ID]` - View performance metrics

**Current Status:**
"""
        metrics = mcp_integration.get_monitoring_metrics()
        for key, value in metrics.items():
            response += f"- **{key.replace('_', ' ').title()}:** {value}\n"
        
        logs_df = mcp_integration.get_session_logs(limit=10)
        df = logs_df
    
    return response, df


def get_real_time_metrics() -> Dict[str, Any]:
    """Get current metrics for real-time display"""
    return mcp_integration.get_monitoring_metrics()


def create_metrics_plot():
    """Create visualization of metrics over time"""
    import plotly.graph_objects as go
    
    logs_df = mcp_integration.get_session_logs(limit=50)
    
    if logs_df.empty or 'latency' not in logs_df.columns:
        # Return empty plot
        fig = go.Figure()
        fig.add_annotation(
            text="No latency data available yet",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    fig = go.Figure()
    
    # Latency over time
    fig.add_trace(go.Scatter(
        x=logs_df['timestamp'],
        y=logs_df['latency'],
        mode='lines+markers',
        name='Latency (s)',
        line=dict(color='#667eea', width=2),
        marker=dict(size=6)
    ))
    
    fig.update_layout(
        title='MCP Server Latency Over Time',
        xaxis_title='Timestamp',
        yaxis_title='Latency (seconds)',
        template='plotly_white',
        hovermode='x unified'
    )
    
    return fig


# Create Gradio interface
with gr.Blocks(css=CUSTOM_CSS, theme=gr.themes.Soft()) as demo:
    gr.HTML('<div class="header-title">🔍 MCP Monitoring Interface</div>')
    
    gr.Markdown("""
    ### Real-time monitoring for Model Context Protocol interactions
    Track contexts, agent observations, and performance metrics with slash commands.
    """)
    
    with gr.Tabs():
        # Tab 1: Chat Interface
        with gr.Tab("💬 Monitor Chat"):
            gr.Markdown("Use slash commands like `/show`, `/context`, `/seen`, or `/metrics` to query the system.")
            
            with gr.Row():
                with gr.Column(scale=2):
                    chatbot = gr.Chatbot(
                        label="Monitoring Console",
                        height=400,
                        type="messages"
                    )
                    msg = gr.Textbox(
                        label="Query",
                        placeholder="Try: /show session=session-001 or /metrics",
                        lines=2
                    )
                    
                    with gr.Row():
                        submit = gr.Button("Send", variant="primary")
                        clear = gr.Button("Clear")
                
                with gr.Column(scale=1):
                    gr.Markdown("### Quick Actions")
                    show_all = gr.Button("📋 Show All Logs")
                    show_metrics = gr.Button("📊 View Metrics")
                    show_context = gr.Button("🔎 Latest Context")
            
            # Data display
            output_df = gr.Dataframe(
                label="Detailed Data",
                wrap=True
            )
            
            # Event handlers
            def respond(message, history):
                # Run async function
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                response, df = loop.run_until_complete(monitor_query(message, history))
                loop.close()
                
                history.append({"role": "user", "content": message})
                history.append({"role": "assistant", "content": response})
                
                return history, df
            
            submit.click(
                respond,
                inputs=[msg, chatbot],
                outputs=[chatbot, output_df]
            )
            
            msg.submit(
                respond,
                inputs=[msg, chatbot],
                outputs=[chatbot, output_df]
            )
            
            clear.click(lambda: ([], None), outputs=[chatbot, output_df])
            
            # Quick action handlers
            show_all.click(
                lambda: respond("/show", []),
                outputs=[chatbot, output_df]
            )
            
            show_metrics.click(
                lambda: respond("/metrics", []),
                outputs=[chatbot, output_df]
            )
            
            show_context.click(
                lambda: respond("/context session=session-001", []),
                outputs=[chatbot, output_df]
            )
        
        # Tab 2: Metrics Dashboard
        with gr.Tab("📊 Metrics Dashboard"):
            gr.Markdown("### Real-time Performance Metrics")
            
            with gr.Row():
                total_requests = gr.Number(label="Total Requests", value=0)
                avg_latency = gr.Number(label="Avg Latency (s)", value=0)
                error_rate = gr.Number(label="Error Rate", value=0)
                total_contexts = gr.Number(label="Total Contexts", value=0)
            
            metrics_plot = gr.Plot(label="Latency Over Time")
            
            refresh_btn = gr.Button("🔄 Refresh Metrics", variant="primary")
            
            def update_metrics():
                metrics = get_real_time_metrics()
                plot = create_metrics_plot()
                return (
                    metrics.get('total_requests', 0),
                    round(metrics.get('avg_latency', 0), 3),
                    round(metrics.get('error_rate', 0), 3),
                    metrics.get('total_contexts', 0),
                    plot
                )
            
            refresh_btn.click(
                update_metrics,
                outputs=[total_requests, avg_latency, error_rate, total_contexts, metrics_plot]
            )
            
            # Auto-update on load
            demo.load(
                update_metrics,
                outputs=[total_requests, avg_latency, error_rate, total_contexts, metrics_plot]
            )
        
        # Tab 3: Session Explorer
        with gr.Tab("🔍 Session Explorer"):
            gr.Markdown("### Explore Session Details")
            
            session_input = gr.Textbox(
                label="Session ID",
                placeholder="e.g., session-001"
            )
            
            explore_btn = gr.Button("Explore Session", variant="primary")
            
            session_info = gr.Markdown()
            session_logs = gr.Dataframe(label="Session Logs")
            
            def explore_session(session_id):
                if not session_id:
                    return "Please enter a session ID", pd.DataFrame()
                
                logs_df = mcp_integration.get_session_logs(session_id=session_id)
                metrics = mcp_integration.get_monitoring_metrics(session_id=session_id)
                
                info = f"""
### Session: {session_id}

**Metrics:**
- Total Requests: {metrics.get('total_requests', 0)}
- Average Latency: {metrics.get('avg_latency', 0):.3f}s
- Total Contexts: {metrics.get('total_contexts', 0)}
- Total Seen Data: {metrics.get('total_seen', 0)}
"""
                return info, logs_df
            
            explore_btn.click(
                explore_session,
                inputs=[session_input],
                outputs=[session_info, session_logs]
            )

    gr.Markdown("""
    ---
    ### About
    This interface provides real-time monitoring for MCP (Model Context Protocol) servers.
    It tracks context provisioning, agent observations, and performance metrics.
    
    **Built with:** Gradio, MCP SDK, and Python
    """)


def launch_interface():
    """Launch the Gradio interface"""
    auth = None
    if config.ENABLE_AUTH and config.GRADIO_AUTH:
        auth = tuple(config.GRADIO_AUTH.split(':'))
    
    demo.launch(
        server_name=config.GRADIO_SERVER_NAME,
        server_port=config.GRADIO_SERVER_PORT,
        share=config.GRADIO_SHARE,
        auth=auth
    )


if __name__ == "__main__":
    print("[STARTING] MCP Monitoring Interface...")
    print(f"Server will be available at http://{config.GRADIO_SERVER_NAME}:{config.GRADIO_SERVER_PORT}")
    launch_interface()
