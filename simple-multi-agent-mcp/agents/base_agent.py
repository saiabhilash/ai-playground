"""
Base Agent Class - Foundation for all agents in the system
"""
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import httpx
from datetime import datetime


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the multi-agent system
    Provides common functionality and interface for agent communication
    """
    
    def __init__(self, agent_name: str, description: str, mcp_server_url: str = "http://localhost:8000"):
        self.agent_name = agent_name
        self.description = description
        self.mcp_server_url = mcp_server_url
        self.logger = logging.getLogger(f"Agent.{agent_name}")
        self.conversation_history: List[Dict[str, Any]] = []
        self.capabilities: List[str] = []
        
    async def initialize(self):
        """Initialize the agent - called once before agent starts working"""
        self.logger.info(f"Initializing agent: {self.agent_name}")
        await self._load_capabilities()
    
    async def _load_capabilities(self):
        """Load agent capabilities from MCP server"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.mcp_server_url}/get_context",
                    json={"context_type": "available_tools"}
                )
                if response.status_code == 200:
                    context = response.json()
                    tools_data = context.get("data", {})
                    self.capabilities = list(tools_data.get("capabilities", {}).keys())
                    self.logger.info(f"Loaded capabilities: {self.capabilities}")
        except Exception as e:
            self.logger.warning(f"Could not load capabilities from MCP server: {e}")
    
    async def call_mcp_tool(self, tool_name: str, method_name: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Call a tool method through the MCP server
        
        Args:
            tool_name: Name of the tool to use
            method_name: Method to call on the tool
            parameters: Parameters to pass to the method
            
        Returns:
            Tool execution result
        """
        if parameters is None:
            parameters = {}
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.mcp_server_url}/execute_tool",
                    json={
                        "tool_name": tool_name,
                        "method_name": method_name,
                        "parameters": parameters
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    self.logger.info(f"Successfully called {tool_name}.{method_name}")
                    return result
                else:
                    self.logger.error(f"MCP tool call failed: {response.status_code} - {response.text}")
                    return {"success": False, "error": f"HTTP {response.status_code}"}
                    
        except Exception as e:
            self.logger.error(f"Error calling MCP tool: {e}")
            return {"success": False, "error": str(e)}
    
    def add_to_history(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """Add message to conversation history"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "content": content,
            "agent": self.agent_name,
            "metadata": metadata or {}
        }
        self.conversation_history.append(entry)
    
    def get_recent_history(self, count: int = 5) -> List[Dict[str, Any]]:
        """Get recent conversation history"""
        return self.conversation_history[-count:]
    
    @abstractmethod
    async def process_message(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process an incoming message and return a response
        
        Args:
            message: The input message to process
            context: Additional context information
            
        Returns:
            Dict containing response and any metadata
        """
        pass
    
    @abstractmethod
    def can_handle(self, message: str) -> bool:
        """
        Determine if this agent can handle the given message
        
        Args:
            message: The message to evaluate
            
        Returns:
            True if the agent can handle this message
        """
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Get agent information"""
        return {
            "name": self.agent_name,
            "description": self.description,
            "capabilities": self.capabilities,
            "conversation_count": len(self.conversation_history)
        }
    
    async def shutdown(self):
        """Cleanup when agent is shutting down"""
        self.logger.info(f"Shutting down agent: {self.agent_name}")
        
    def __str__(self) -> str:
        return f"{self.agent_name}: {self.description}"
