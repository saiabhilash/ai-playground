"""
Task Agent - Coordinator agent for task planning and delegation
"""
import re
from typing import Dict, Any, List
from .base_agent import BaseAgent


class TaskAgent(BaseAgent):
    """
    Agent specialized in task coordination, planning, and delegation
    Acts as the main coordinator for complex tasks requiring multiple agents
    """
    
    def __init__(self, mcp_server_url: str = "http://localhost:8000"):
        super().__init__(
            agent_name="TaskAgent",
            description="Task coordinator and planner that orchestrates multi-agent workflows",
            mcp_server_url=mcp_server_url
        )
        
        # Keywords that indicate this agent should handle the message
        self.task_keywords = [
            'plan', 'organize', 'coordinate', 'manage', 'schedule', 'task',
            'workflow', 'process', 'steps', 'breakdown', 'delegate',
            'help me', 'can you', 'please', 'need to', 'want to'
        ]
        
        # Available agents for delegation
        self.available_agents = []
    
    def register_agent(self, agent):
        """Register an agent for potential delegation"""
        if agent.agent_name != self.agent_name:  # Don't register self
            self.available_agents.append(agent)
            self.logger.info(f"Registered agent: {agent.agent_name}")
    
    def can_handle(self, message: str) -> bool:
        """
        Determine if this message requires task coordination
        This agent can handle general requests and coordination tasks
        """
        message_lower = message.lower()
        
        # Check for task coordination keywords
        has_task_keywords = any(keyword in message_lower for keyword in self.task_keywords)
        
        # Check for multi-step requests
        has_multi_step = any(word in message_lower for word in ['and', 'then', 'also', 'plus', 'both'])
        
        # Check for general requests that need coordination
        has_general_request = any(phrase in message_lower for phrase in [
            'help me', 'can you', 'i need', 'please', 'how do i'
        ])
        
        # This agent handles coordination, so it can potentially handle any message
        # that doesn't clearly belong to a specialized agent
        return has_task_keywords or has_multi_step or has_general_request
    
    async def process_message(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process task coordination and planning requests
        """
        self.add_to_history("user", message)
        
        try:
            # Analyze the message to determine what needs to be done
            task_analysis = await self._analyze_task(message)
            
            # Check if we can delegate to other agents
            if self.available_agents:
                delegation_result = await self._delegate_if_possible(message, task_analysis)
                if delegation_result:
                    return delegation_result
            
            # Handle the task ourselves if no delegation possible
            result = await self._handle_coordination_task(message, task_analysis)
            response = self._format_coordination_response(result, task_analysis)
            
            self.add_to_history("assistant", response["content"], {"task_analysis": task_analysis})
            return response
            
        except Exception as e:
            error_response = {
                "agent": self.agent_name,
                "content": f"I encountered an error while processing your task: {str(e)}",
                "success": False,
                "error": str(e)
            }
            self.add_to_history("assistant", error_response["content"], {"error": str(e)})
            return error_response
    
    async def _analyze_task(self, message: str) -> Dict[str, Any]:
        """
        Analyze the message to understand what task is being requested
        """
        message_lower = message.lower()
        
        analysis = {
            "original_message": message,
            "task_type": "general",
            "requires_math": False,
            "requires_text_analysis": False,
            "requires_coordination": False,
            "complexity": "simple",
            "steps": []
        }
        
        # Check for mathematical requirements
        math_indicators = ['calculate', 'solve', 'math', 'equation', 'number', '+', '-', '*', '/', '=']
        analysis["requires_math"] = any(indicator in message_lower for indicator in math_indicators)
        
        # Check for text analysis requirements
        text_indicators = ['analyze', 'sentiment', 'text', 'words', 'count', 'summarize']
        analysis["requires_text_analysis"] = any(indicator in message_lower for indicator in text_indicators)
        
        # Check for coordination requirements (multiple tasks)
        coordination_indicators = ['and', 'then', 'also', 'plus', 'both', 'first', 'second', 'next']
        analysis["requires_coordination"] = any(indicator in message_lower for indicator in coordination_indicators)
        
        # Determine complexity
        if analysis["requires_coordination"] or (analysis["requires_math"] and analysis["requires_text_analysis"]):
            analysis["complexity"] = "complex"
        elif analysis["requires_math"] or analysis["requires_text_analysis"]:
            analysis["complexity"] = "medium"
        
        # Extract potential steps
        analysis["steps"] = self._extract_steps(message)
        
        return analysis
    
    def _extract_steps(self, message: str) -> List[str]:
        """
        Extract individual steps or tasks from the message
        """
        steps = []
        
        # Look for numbered steps
        numbered_steps = re.findall(r'\d+[.)]\s*([^.!?]*[.!?]?)', message)
        if numbered_steps:
            steps.extend([step.strip() for step in numbered_steps])
        
        # Look for steps separated by common connectors
        if not steps:
            # Split on connectors
            parts = re.split(r'\s+(?:and|then|also|plus|next|after that)\s+', message, flags=re.IGNORECASE)
            if len(parts) > 1:
                steps.extend([part.strip() for part in parts])
        
        # If no clear steps found, treat the whole message as one step
        if not steps:
            steps = [message.strip()]
        
        return steps
    
    async def _delegate_if_possible(self, message: str, task_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Try to delegate the task to a specialized agent if appropriate
        """
        # Find the best agent for this task
        best_agent = None
        
        # Check if any specialized agent can handle this
        for agent in self.available_agents:
            if agent.can_handle(message):
                best_agent = agent
                break
        
        if best_agent:
            self.logger.info(f"Delegating task to {best_agent.agent_name}")
            
            # Delegate to the specialized agent
            result = await best_agent.process_message(message)
            
            # Add our coordination context
            result["delegated_to"] = best_agent.agent_name
            result["coordinator"] = self.agent_name
            
            return result
        
        return None
    
    async def _handle_coordination_task(self, message: str, task_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle coordination tasks that we can't delegate
        """
        if task_analysis["complexity"] == "complex":
            return await self._handle_complex_task(message, task_analysis)
        else:
            return await self._handle_simple_task(message, task_analysis)
    
    async def _handle_complex_task(self, message: str, task_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle complex multi-step tasks
        """
        steps = task_analysis["steps"]
        results = []
        
        for i, step in enumerate(steps, 1):
            step_result = {
                "step_number": i,
                "step_description": step,
                "status": "planned"
            }
            
            # Try to delegate each step to appropriate agents
            delegated = False
            for agent in self.available_agents:
                if agent.can_handle(step):
                    try:
                        agent_result = await agent.process_message(step)
                        step_result["status"] = "completed"
                        step_result["result"] = agent_result
                        step_result["handled_by"] = agent.agent_name
                        delegated = True
                        break
                    except Exception as e:
                        step_result["status"] = "failed"
                        step_result["error"] = str(e)
            
            if not delegated:
                step_result["status"] = "needs_attention"
                step_result["note"] = "No specialized agent available for this step"
            
            results.append(step_result)
        
        return {
            "success": True,
            "task_type": "complex_coordination",
            "total_steps": len(steps),
            "completed_steps": len([r for r in results if r["status"] == "completed"]),
            "step_results": results
        }
    
    async def _handle_simple_task(self, message: str, task_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle simple coordination tasks
        """
        # Get current time for context
        time_result = await self.call_mcp_tool("utility", "get_current_time")
        current_time = time_result.get("result", "unknown") if time_result.get("success") else "unknown"
        
        return {
            "success": True,
            "task_type": "simple_coordination",
            "message": message,
            "analysis": task_analysis,
            "timestamp": current_time,
            "available_agents": [agent.agent_name for agent in self.available_agents]
        }
    
    def _format_coordination_response(self, result: Dict[str, Any], task_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format the coordination response
        """
        if result.get("task_type") == "complex_coordination":
            return self._format_complex_response(result)
        else:
            return self._format_simple_response(result, task_analysis)
    
    def _format_complex_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format response for complex multi-step tasks
        """
        total_steps = result.get("total_steps", 0)
        completed_steps = result.get("completed_steps", 0)
        step_results = result.get("step_results", [])
        
        content = f"**Task Coordination Complete**\n\n"
        content += f"**Progress:** {completed_steps}/{total_steps} steps completed\n\n"
        
        for step_result in step_results:
            step_num = step_result["step_number"]
            status = step_result["status"]
            description = step_result["step_description"]
            
            if status == "completed":
                content += f"✅ **Step {step_num}:** {description}\n"
                handled_by = step_result.get("handled_by", "unknown")
                content += f"   *Handled by: {handled_by}*\n\n"
            elif status == "failed":
                content += f"❌ **Step {step_num}:** {description}\n"
                error = step_result.get("error", "unknown error")
                content += f"   *Error: {error}*\n\n"
            else:
                content += f"⏳ **Step {step_num}:** {description}\n"
                note = step_result.get("note", "Pending")
                content += f"   *Status: {note}*\n\n"
        
        return {
            "agent": self.agent_name,
            "content": content,
            "success": True,
            "result": result
        }
    
    def _format_simple_response(self, result: Dict[str, Any], task_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format response for simple tasks
        """
        message = result.get("message", "")
        available_agents = result.get("available_agents", [])
        
        content = f"**Task Analysis Complete**\n\n"
        content += f"**Your request:** {message}\n\n"
        
        if task_analysis["requires_math"]:
            content += "🔢 This task appears to involve mathematical calculations.\n"
        if task_analysis["requires_text_analysis"]:
            content += "📝 This task appears to involve text analysis.\n"
        
        content += f"**Available specialized agents:** {', '.join(available_agents)}\n\n"
        
        if available_agents:
            content += "I can coordinate with these specialized agents to help you with specific tasks. "
            content += "Try asking something more specific, like:\n"
            content += "• 'Calculate the sum of 15 and 27' (for math tasks)\n"
            content += "• 'Analyze the sentiment of this text: ...' (for text tasks)\n"
        else:
            content += "I'm ready to help coordinate tasks, but no specialized agents are currently available."
        
        return {
            "agent": self.agent_name,
            "content": content,
            "success": True,
            "result": result
        }
