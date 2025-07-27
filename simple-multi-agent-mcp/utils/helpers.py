"""
Helper functions for the multi-agent system
"""
import os
import asyncio
import signal
from typing import Dict, Any, Optional
from datetime import datetime


def load_environment() -> Dict[str, str]:
    """
    Load environment variables from .env file if available
    
    Returns:
        Dict of environment variables
    """
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        return {
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
            "AZURE_OPENAI_ENDPOINT": os.getenv("AZURE_OPENAI_ENDPOINT", ""),
            "AZURE_OPENAI_API_KEY": os.getenv("AZURE_OPENAI_API_KEY", ""),
            "DEPLOYMENT_NAME": os.getenv("DEPLOYMENT_NAME", "gpt-4o"),
            "MCP_SERVER_HOST": os.getenv("MCP_SERVER_HOST", "localhost"),
            "MCP_SERVER_PORT": os.getenv("MCP_SERVER_PORT", "8000"),
            "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO")
        }
    except ImportError:
        # dotenv not available, just read from environment
        return {
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
            "AZURE_OPENAI_ENDPOINT": os.getenv("AZURE_OPENAI_ENDPOINT", ""),
            "AZURE_OPENAI_API_KEY": os.getenv("AZURE_OPENAI_API_KEY", ""),
            "DEPLOYMENT_NAME": os.getenv("DEPLOYMENT_NAME", "gpt-4o"),
            "MCP_SERVER_HOST": os.getenv("MCP_SERVER_HOST", "localhost"),
            "MCP_SERVER_PORT": os.getenv("MCP_SERVER_PORT", "8000"),
            "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO")
        }


def validate_environment(env_vars: Dict[str, str]) -> bool:
    """
    Validate that required environment variables are set
    
    Args:
        env_vars: Dictionary of environment variables
        
    Returns:
        True if all required variables are set
    """
    required_vars = ["MCP_SERVER_HOST", "MCP_SERVER_PORT"]
    
    missing_vars = []
    for var in required_vars:
        if not env_vars.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    return True


def format_response(response: Dict[str, Any]) -> str:
    """
    Format agent response for display
    
    Args:
        response: Agent response dictionary
        
    Returns:
        Formatted string for display
    """
    agent_name = response.get("agent", "Unknown")
    content = response.get("content", "")
    success = response.get("success", True)
    
    # Add status indicator
    status_icon = "✅" if success else "❌"
    
    # Format the response
    formatted = f"{status_icon} **{agent_name}**\n"
    formatted += f"{content}\n"
    
    # Add metadata if available
    orchestration = response.get("orchestration", {})
    if orchestration:
        formatted += f"\n*Agent: {orchestration.get('selected_agent', agent_name)}*"
    
    return formatted


def create_welcome_message() -> str:
    """
    Create a welcome message for the system
    
    Returns:
        Welcome message string
    """
    welcome = """
🤖 **Simple Multi-Agent System with MCP Server**

Welcome! I'm a multi-agent system that can help you with various tasks:

**Available Agents:**
• 🔢 **Math Agent** - Calculations, equations, and mathematical analysis
• 📝 **Text Agent** - Text processing, sentiment analysis, and content manipulation  
• 🎯 **Task Agent** - Task coordination and planning

**Example Commands:**
• "Calculate the sum of 15 and 27"
• "Solve the equation 2x + 5 = 15"
• "Analyze the sentiment of this text: 'I love sunny days'"
• "Count the words in this sentence"
• "Help me plan a task to solve math problems and analyze text"

Type your request and I'll route it to the most appropriate agent!
Type 'exit' to quit, 'status' for system information, or 'help' for more commands.
"""
    return welcome


def create_help_message() -> str:
    """
    Create a help message with available commands
    
    Returns:
        Help message string
    """
    help_msg = """
**Available Commands:**

**Math Operations:**
• "Calculate X + Y" (or -, *, /)
• "Solve equation: 2x + 5 = 15"
• "What's the square root of 25?"
• "Raise 2 to the power of 8"

**Text Analysis:**
• "Analyze sentiment: 'your text here'"
• "Count words in: 'your text here'"
• "Summarize this text: 'your text here'"
• "Extract numbers from: 'your text here'"

**Task Coordination:**
• "Help me plan..."
• "Can you coordinate..."
• "I need to do X and Y"

**System Commands:**
• 'status' - Show system status
• 'help' - Show this help message
• 'exit' - Quit the application

**Tips:**
• The system automatically routes your request to the best agent
• You can combine multiple tasks in one message
• Use quotes around text you want analyzed
"""
    return help_msg


async def wait_for_mcp_server(host: str, port: int, max_attempts: int = 30, delay: float = 1.0) -> bool:
    """
    Wait for MCP server to be available
    
    Args:
        host: Server host
        port: Server port  
        max_attempts: Maximum connection attempts
        delay: Delay between attempts in seconds
        
    Returns:
        True if server is available, False if timeout
    """
    import httpx
    
    url = f"http://{host}:{port}/"
    
    for attempt in range(max_attempts):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=2.0)
                if response.status_code == 200:
                    return True
        except Exception:
            pass
        
        if attempt < max_attempts - 1:
            await asyncio.sleep(delay)
    
    return False


def setup_signal_handlers(shutdown_callback):
    """
    Setup signal handlers for graceful shutdown
    
    Args:
        shutdown_callback: Function to call on shutdown signal
    """
    def signal_handler(signum, frame):
        print(f"\nReceived signal {signum}. Shutting down gracefully...")
        asyncio.create_task(shutdown_callback())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def get_timestamp() -> str:
    """Get current timestamp as ISO string"""
    return datetime.now().isoformat()


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to specified length with ellipsis
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."
