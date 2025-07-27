"""
Multi-Agent System Orchestrator
Manages the coordination and communication between agents
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent
from agents.task_agent import TaskAgent
from agents.math_agent import MathAgent
from agents.text_agent import TextAgent


class AgentOrchestrator:
    """
    Main orchestrator for the multi-agent system
    Manages agent lifecycle, message routing, and coordination
    """
    
    def __init__(self, mcp_server_url: str = "http://localhost:8000"):
        self.mcp_server_url = mcp_server_url
        self.agents: Dict[str, BaseAgent] = {}
        self.task_agent: Optional[TaskAgent] = None
        self.logger = logging.getLogger("Orchestrator")
        self.conversation_history: List[Dict[str, Any]] = []
        self.is_running = False
    
    async def initialize(self):
        """Initialize the orchestrator and all agents"""
        self.logger.info("Initializing Multi-Agent System...")
        
        # Create specialized agents
        math_agent = MathAgent(self.mcp_server_url)
        text_agent = TextAgent(self.mcp_server_url)
        
        # Create task coordinator agent
        self.task_agent = TaskAgent(self.mcp_server_url)
        
        # Register agents
        self.agents = {
            math_agent.agent_name: math_agent,
            text_agent.agent_name: text_agent,
            self.task_agent.agent_name: self.task_agent
        }
        
        # Initialize all agents
        for agent in self.agents.values():
            await agent.initialize()
        
        # Register specialized agents with the task coordinator
        for agent_name, agent in self.agents.items():
            if agent_name != self.task_agent.agent_name:
                self.task_agent.register_agent(agent)
        
        self.is_running = True
        self.logger.info(f"Initialized {len(self.agents)} agents: {list(self.agents.keys())}")
    
    async def process_message(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a user message by routing it to the appropriate agent
        
        Args:
            message: User input message
            context: Additional context information
            
        Returns:
            Agent response with metadata
        """
        if not self.is_running:
            return {
                "agent": "System",
                "content": "System is not initialized. Please wait for initialization to complete.",
                "success": False,
                "error": "System not initialized"
            }
        
        self.logger.info(f"Processing message: {message[:100]}...")
        
        # Add to conversation history
        self._add_to_history("user", message, {"timestamp": self._get_timestamp()})
        
        try:
            # Find the best agent to handle this message
            selected_agent = await self._select_agent(message)
            
            if not selected_agent:
                # If no specific agent can handle it, use the task coordinator
                selected_agent = self.task_agent
            
            self.logger.info(f"Selected agent: {selected_agent.agent_name}")
            
            # Process message with selected agent
            response = await selected_agent.process_message(message, context)
            
            # Add metadata about orchestration
            response["orchestration"] = {
                "selected_agent": selected_agent.agent_name,
                "total_agents": len(self.agents),
                "conversation_turn": len(self.conversation_history)
            }
            
            # Add to conversation history
            self._add_to_history("assistant", response.get("content", ""), {
                "agent": selected_agent.agent_name,
                "success": response.get("success", True),
                "timestamp": self._get_timestamp()
            })
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            error_response = {
                "agent": "System",
                "content": f"I encountered an error while processing your request: {str(e)}",
                "success": False,
                "error": str(e),
                "orchestration": {
                    "error": True,
                    "timestamp": self._get_timestamp()
                }
            }
            
            self._add_to_history("assistant", error_response["content"], {
                "agent": "System",
                "error": str(e),
                "timestamp": self._get_timestamp()
            })
            
            return error_response
    
    async def _select_agent(self, message: str) -> Optional[BaseAgent]:
        """
        Select the most appropriate agent to handle the message
        
        Args:
            message: User input message
            
        Returns:
            Selected agent or None if no specific agent can handle it
        """
        # Score each agent's ability to handle the message
        agent_scores = {}
        
        for agent_name, agent in self.agents.items():
            if agent_name != self.task_agent.agent_name:  # Skip task agent for now
                try:
                    can_handle = agent.can_handle(message)
                    
                    # Calculate confidence score based on agent type and message content
                    score = 0.0
                    if can_handle:
                        message_lower = message.lower()
                        
                        # Text agent gets higher score for text-specific requests
                        if agent_name == "TextAgent":
                            text_indicators = ['sentiment', 'analyze', 'text', 'words', 'count', 'extract']
                            text_score = sum(1 for indicator in text_indicators if indicator in message_lower)
                            score = 0.8 + (text_score * 0.1)
                        
                        # Math agent gets higher score for math-specific requests
                        elif agent_name == "MathAgent":
                            math_indicators = ['calculate', 'solve', 'equation', 'math', '+', '-', '*', '/', '=']
                            math_score = sum(1 for indicator in math_indicators if indicator in message_lower)
                            score = 0.6 + (math_score * 0.1)
                        
                        else:
                            score = 1.0
                    
                    agent_scores[agent_name] = score
                    self.logger.debug(f"Agent {agent_name} score: {score}")
                    
                except Exception as e:
                    self.logger.warning(f"Error checking if {agent_name} can handle message: {e}")
                    agent_scores[agent_name] = 0.0
        
        # Find the agent with the highest score
        if agent_scores:
            best_agent_name = max(agent_scores, key=agent_scores.get)
            best_score = agent_scores[best_agent_name]
            
            self.logger.debug(f"Best agent: {best_agent_name} with score {best_score}")
            
            if best_score > 0:
                return self.agents[best_agent_name]
        
        return None
    
    def _add_to_history(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """Add entry to conversation history"""
        entry = {
            "role": role,
            "content": content,
            "metadata": metadata or {}
        }
        self.conversation_history.append(entry)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp string"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        agent_status = {}
        for agent_name, agent in self.agents.items():
            agent_status[agent_name] = agent.get_info()
        
        return {
            "is_running": self.is_running,
            "total_agents": len(self.agents),
            "conversation_turns": len(self.conversation_history),
            "agents": agent_status,
            "mcp_server_url": self.mcp_server_url
        }
    
    def get_conversation_history(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation history"""
        return self.conversation_history[-count:]
    
    async def shutdown(self):
        """Shutdown the orchestrator and all agents"""
        self.logger.info("Shutting down Multi-Agent System...")
        
        # Shutdown all agents
        for agent in self.agents.values():
            try:
                await agent.shutdown()
            except Exception as e:
                self.logger.warning(f"Error shutting down agent {agent.agent_name}: {e}")
        
        self.is_running = False
        self.logger.info("System shutdown complete")
    
    def get_agent_capabilities(self) -> Dict[str, List[str]]:
        """Get capabilities of all agents"""
        capabilities = {}
        for agent_name, agent in self.agents.items():
            capabilities[agent_name] = {
                "description": agent.description,
                "capabilities": agent.capabilities
            }
        return capabilities
