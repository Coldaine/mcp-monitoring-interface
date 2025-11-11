"""
MCP Server Integration Layer
Handles communication with MCP servers and context logging
"""
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import httpx

import config
from utils import LogManager

class MCPIntegration:
    """
    Integration layer for MCP (Model Context Protocol) servers
    Captures contexts, agent observations, and sampling operations
    """
    
    def __init__(self, server_url: str = None, api_key: str = None):
        self.server_url = server_url or config.MCP_SERVER_URL
        self.api_key = api_key or config.MCP_API_KEY
        self.log_manager = LogManager()
        self.active_sessions = {}
    
    async def call_tool(self, 
                       tool_name: str, 
                       parameters: Dict[str, Any],
                       session_id: str = None) -> Dict[str, Any]:
        """
        Call an MCP tool and log the interaction
        """
        session_id = session_id or f"session-{datetime.now().timestamp()}"
        
        # Prepare request
        request_data = {
            "tool": tool_name,
            "parameters": parameters,
            "session_id": session_id
        }
        
        start_time = datetime.now()
        
        try:
            async with httpx.AsyncClient() as client:
                headers = {}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                response = await client.post(
                    f"{self.server_url}/tools/{tool_name}",
                    json=request_data,
                    headers=headers,
                    timeout=30.0
                )
                
                response.raise_for_status()
                result = response.json()
                
                # Calculate latency
                latency = (datetime.now() - start_time).total_seconds()
                
                # Log the tool call
                self.log_manager.add_log({
                    'type': 'tool_call',
                    'session_id': session_id,
                    'tool_name': tool_name,
                    'parameters': parameters,
                    'result': result,
                    'latency': latency,
                    'status': 'success'
                })
                
                return result
                
        except Exception as e:
            latency = (datetime.now() - start_time).total_seconds()
            
            # Log the error
            self.log_manager.add_log({
                'type': 'error',
                'session_id': session_id,
                'tool_name': tool_name,
                'error': str(e),
                'latency': latency,
                'status': 'error'
            })
            
            return {'error': str(e)}
    
    async def get_provided_context(self, 
                                   session_id: str,
                                   task_id: str = None) -> Dict[str, Any]:
        """
        Retrieve context that was provided to the agent
        (e.g., sampled repo files, augmented data)
        """
        try:
            async with httpx.AsyncClient() as client:
                headers = {}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                params = {"session_id": session_id}
                if task_id:
                    params["task_id"] = task_id
                
                response = await client.get(
                    f"{self.server_url}/context",
                    params=params,
                    headers=headers
                )
                
                response.raise_for_status()
                context_data = response.json()
                
                # Log context retrieval
                self.log_manager.add_log({
                    'type': 'context',
                    'session_id': session_id,
                    'task_id': task_id,
                    'context_data': context_data,
                    'status': 'retrieved'
                })
                
                return context_data
                
        except Exception as e:
            return {'error': f'Failed to retrieve context: {str(e)}'}
    
    async def get_agent_seen_data(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get data that the agent has actually processed
        (filtered snippets, selected commits, etc.)
        """
        try:
            async with httpx.AsyncClient() as client:
                headers = {}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                response = await client.get(
                    f"{self.server_url}/agent-observations",
                    params={"session_id": session_id},
                    headers=headers
                )
                
                response.raise_for_status()
                seen_data = response.json()
                
                # Log seen data retrieval
                for item in seen_data:
                    self.log_manager.add_log({
                        'type': 'seen',
                        'session_id': session_id,
                        'action': item.get('action', 'unknown'),
                        'details': item.get('details', ''),
                        'timestamp': item.get('timestamp', datetime.now().isoformat())
                    })
                
                return seen_data
                
        except Exception as e:
            return [{'error': f'Failed to retrieve seen data: {str(e)}'}]
    
    async def sample_repo_context(self, 
                                  task: str,
                                  repo_path: str = None,
                                  session_id: str = None) -> Dict[str, Any]:
        """
        Sample repository context for a given task
        This is your core repo-augmentation feature
        """
        session_id = session_id or f"session-{datetime.now().timestamp()}"
        
        parameters = {
            "task": task,
            "repo_path": repo_path
        }
        
        start_time = datetime.now()
        
        try:
            # Simulate sampling logic (replace with actual implementation)
            sampled_context = {
                "task": task,
                "files": self._sample_relevant_files(task, repo_path),
                "commits": self._sample_relevant_commits(task, repo_path),
                "tokens_used": 0,  # Calculate based on actual content
                "sampling_strategy": "relevance-based"
            }
            
            # Calculate tokens
            sampled_context["tokens_used"] = self._estimate_tokens(sampled_context)
            
            latency = (datetime.now() - start_time).total_seconds()
            
            # Log the sampling operation
            self.log_manager.add_log({
                'type': 'context',
                'session_id': session_id,
                'task_id': task,
                'details': 'Sampled repository context',
                'files': [f['path'] for f in sampled_context['files']],
                'commits': len(sampled_context['commits']),
                'tokens': sampled_context['tokens_used'],
                'latency': latency
            })
            
            return sampled_context
            
        except Exception as e:
            return {'error': f'Sampling failed: {str(e)}'}
    
    def _sample_relevant_files(self, task: str, repo_path: str = None) -> List[Dict[str, str]]:
        """Sample relevant files based on task (placeholder)"""
        # This would use actual file analysis
        return [
            {"path": "src/main.py", "relevance": 0.95},
            {"path": "config/settings.yml", "relevance": 0.80},
            {"path": "tests/test_main.py", "relevance": 0.70}
        ]
    
    def _sample_relevant_commits(self, task: str, repo_path: str = None) -> List[Dict[str, str]]:
        """Sample relevant commits based on task (placeholder)"""
        # This would use actual git history analysis
        return [
            {"hash": "abc123", "message": "Fix deployment issue", "relevance": 0.90},
            {"hash": "def456", "message": "Update config", "relevance": 0.75}
        ]
    
    def _estimate_tokens(self, context: Dict[str, Any]) -> int:
        """Estimate token count for context"""
        # Rough estimation (replace with actual tokenizer)
        text = json.dumps(context)
        return len(text.split()) * 1.3  # Approximate tokens
    
    def get_monitoring_metrics(self, session_id: str = None) -> Dict[str, Any]:
        """
        Get monitoring metrics for dashboards
        Leverages Gradio's built-in /monitoring endpoint concepts
        """
        return self.log_manager.get_metrics(session_id=session_id)
    
    def get_session_logs(self, 
                        session_id: str = None,
                        task_id: str = None,
                        limit: int = None):
        """Get logs for monitoring interface"""
        return self.log_manager.get_logs(
            session_id=session_id,
            task_id=task_id,
            limit=limit
        )


# Singleton instance
mcp_integration = MCPIntegration()
