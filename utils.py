"""
Utility functions for MCP Monitoring Interface
Handles logging, data processing, and helper operations
"""
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import deque
import config

class LogManager:
    """Manages session logs and context tracking"""
    
    def __init__(self, max_entries: int = None):
        self.max_entries = max_entries or config.MAX_LOG_ENTRIES
        self.logs = deque(maxlen=self.max_entries)
        self.session_data = {}
    
    def add_log(self, log_entry: Dict[str, Any]) -> None:
        """Add a new log entry with timestamp"""
        log_entry['timestamp'] = datetime.now().isoformat()
        self.logs.append(log_entry)
    
    def get_logs(self, 
                 session_id: Optional[str] = None,
                 task_id: Optional[str] = None,
                 limit: Optional[int] = None) -> pd.DataFrame:
        """Retrieve logs as DataFrame with optional filtering"""
        filtered_logs = list(self.logs)
        
        if session_id:
            filtered_logs = [log for log in filtered_logs if log.get('session_id') == session_id]
        
        if task_id:
            filtered_logs = [log for log in filtered_logs if log.get('task_id') == task_id]
        
        if limit:
            filtered_logs = filtered_logs[-limit:]
        
        if not filtered_logs:
            return pd.DataFrame(columns=['timestamp', 'type', 'session_id', 'task_id', 'details'])
        
        return pd.DataFrame(filtered_logs)
    
    def get_context_for_session(self, session_id: str) -> Dict[str, Any]:
        """Get all context data for a specific session"""
        context_logs = [log for log in self.logs 
                       if log.get('session_id') == session_id 
                       and log.get('type') == 'context']
        
        return {
            'session_id': session_id,
            'contexts': context_logs,
            'total_contexts': len(context_logs)
        }
    
    def get_seen_data(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all data that the agent has processed"""
        seen_logs = [log for log in self.logs 
                    if log.get('session_id') == session_id 
                    and log.get('type') == 'seen']
        
        return seen_logs
    
    def get_metrics(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Calculate performance metrics"""
        logs_df = self.get_logs(session_id=session_id)
        
        if logs_df.empty:
            return {
                'total_requests': 0,
                'avg_latency': 0,
                'error_rate': 0,
                'total_contexts': 0
            }
        
        metrics = {
            'total_requests': len(logs_df),
            'avg_latency': logs_df['latency'].mean() if 'latency' in logs_df.columns else 0,
            'error_rate': (logs_df['type'] == 'error').sum() / len(logs_df) if len(logs_df) > 0 else 0,
            'total_contexts': (logs_df['type'] == 'context').sum(),
            'total_seen': (logs_df['type'] == 'seen').sum()
        }
        
        return metrics
    
    def cleanup_old_logs(self, retention_days: int = None) -> int:
        """Remove logs older than retention period"""
        retention_days = retention_days or config.LOG_RETENTION_DAYS
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        initial_count = len(self.logs)
        self.logs = deque(
            [log for log in self.logs 
             if datetime.fromisoformat(log['timestamp']) > cutoff_date],
            maxlen=self.max_entries
        )
        
        return initial_count - len(self.logs)


def format_context_for_display(context: Dict[str, Any]) -> str:
    """Format context data for display in chat interface"""
    if not context:
        return "No context available"
    
    formatted = f"**Context Type:** {context.get('type', 'Unknown')}\n\n"
    
    if 'files' in context:
        formatted += "**Files Provided:**\n"
        for file in context['files']:
            formatted += f"- {file.get('path', 'Unknown path')}\n"
    
    if 'commits' in context:
        formatted += f"\n**Commits:** {len(context['commits'])} commits\n"
    
    if 'tokens' in context:
        formatted += f"\n**Tokens Used:** {context['tokens']}\n"
    
    return formatted


def format_seen_data_for_display(seen_data: List[Dict[str, Any]]) -> str:
    """Format seen data for display"""
    if not seen_data:
        return "No data processed yet"
    
    formatted = "**Agent Processing History:**\n\n"
    
    for idx, item in enumerate(seen_data, 1):
        formatted += f"{idx}. **{item.get('action', 'Unknown action')}**\n"
        formatted += f"   - Timestamp: {item.get('timestamp', 'N/A')}\n"
        if 'details' in item:
            formatted += f"   - Details: {item['details']}\n"
        formatted += "\n"
    
    return formatted


def create_metrics_dataframe(metrics: Dict[str, Any]) -> pd.DataFrame:
    """Convert metrics dict to DataFrame for display"""
    return pd.DataFrame([metrics]).T.reset_index()


def parse_slash_command(command_text: str) -> Dict[str, Any]:
    """Parse slash command arguments"""
    parts = command_text.strip().split()
    
    parsed = {
        'action': 'show',  # Default action
        'target': 'all',
        'filters': {}
    }
    
    if not parts:
        return parsed
    
    # First part is typically the action
    if parts[0] in ['show', 'metrics', 'context', 'seen', 'search']:
        parsed['action'] = parts[0]
        parts = parts[1:]
    
    # Parse remaining arguments
    for part in parts:
        if '=' in part:
            key, value = part.split('=', 1)
            parsed['filters'][key] = value
        else:
            parsed['target'] = part
    
    return parsed


def generate_sample_logs() -> List[Dict[str, Any]]:
    """Generate sample logs for testing"""
    sample_logs = [
        {
            'type': 'context',
            'session_id': 'session-001',
            'task_id': 'task-dev-123',
            'details': 'Sampled repository context for DevOps task',
            'files': ['src/deploy.py', 'config/prod.yml'],
            'tokens': 1250,
            'latency': 0.45
        },
        {
            'type': 'seen',
            'session_id': 'session-001',
            'task_id': 'task-dev-123',
            'action': 'Filtered commits',
            'details': 'Processed commits from hash abc123 to def456',
            'latency': 0.12
        },
        {
            'type': 'context',
            'session_id': 'session-002',
            'task_id': 'task-dev-124',
            'details': 'Augmented codebase with recent changes',
            'commits': 15,
            'tokens': 2100,
            'latency': 0.78
        }
    ]
    
    return sample_logs
