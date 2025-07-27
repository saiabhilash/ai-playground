"""
Simple Multi-Agent System with MCP Server
Main application entry point
"""
import asyncio
import sys
import os
from typing import Optional

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.logger import setup_logging, get_logger
from core.orchestrator import AgentOrchestrator
from mcp_server.server import start_mcp_server
from utils.helpers import (
    load_environment, validate_environment, format_response,
    create_welcome_message, create_help_message, wait_for_mcp_server,
    setup_signal_handlers
)


class MultiAgentApp:
    """
    Main application class for the multi-agent system
    """
    
    def __init__(self):
        self.orchestrator: Optional[AgentOrchestrator] = None
        self.mcp_server_task: Optional[asyncio.Task] = None
        self.logger = get_logger("MultiAgentApp")
        self.running = False
        
        # Load configuration
        self.env_vars = load_environment()
        self.mcp_host = self.env_vars.get("MCP_SERVER_HOST", "localhost")
        self.mcp_port = int(self.env_vars.get("MCP_SERVER_PORT", "8000"))
        self.mcp_url = f"http://{self.mcp_host}:{self.mcp_port}"
    
    async def initialize(self):
        """Initialize the application"""
        self.logger.info("Starting Simple Multi-Agent System...")
        
        # Validate environment
        if not validate_environment(self.env_vars):
            raise Exception("Environment validation failed")
        
        # Start MCP server
        self.logger.info(f"Starting MCP server on {self.mcp_host}:{self.mcp_port}")
        self.mcp_server_task = asyncio.create_task(
            start_mcp_server(self.mcp_host, self.mcp_port)
        )
        
        # Wait for MCP server to be ready
        self.logger.info("Waiting for MCP server to be ready...")
        if not await wait_for_mcp_server(self.mcp_host, self.mcp_port):
            raise Exception("MCP server failed to start")
        
        self.logger.info("MCP server is ready")
        
        # Initialize orchestrator
        self.orchestrator = AgentOrchestrator(self.mcp_url)
        await self.orchestrator.initialize()
        
        self.running = True
        self.logger.info("Application initialization complete")
    
    async def run_interactive(self):
        """Run the application in interactive mode"""
        print(create_welcome_message())
        
        while self.running:
            try:
                # Get user input
                user_input = input("\n💬 You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.lower() == 'exit':
                    print("\n👋 Goodbye!")
                    break
                elif user_input.lower() == 'help':
                    print(create_help_message())
                    continue
                elif user_input.lower() == 'status':
                    await self._show_status()
                    continue
                
                # Process message with orchestrator
                print(f"\n🤔 Processing...")
                response = await self.orchestrator.process_message(user_input)
                
                # Format and display response
                formatted_response = format_response(response)
                print(f"\n{formatted_response}")
                
            except KeyboardInterrupt:
                print("\n\n⚠️  Received interrupt signal")
                break
            except EOFError:
                print("\n\n⚠️  End of input received")
                break
            except Exception as e:
                self.logger.error(f"Error in interactive loop: {e}")
                print(f"\n❌ Error: {str(e)}")
    
    async def _show_status(self):
        """Show system status"""
        if self.orchestrator:
            status = self.orchestrator.get_system_status()
            
            print("\n📊 **System Status**")
            print(f"• Running: {'✅ Yes' if status['is_running'] else '❌ No'}")
            print(f"• Total Agents: {status['total_agents']}")
            print(f"• Conversation Turns: {status['conversation_turns']}")
            print(f"• MCP Server: {self.mcp_url}")
            
            print("\n🤖 **Agents:**")
            for agent_name, agent_info in status['agents'].items():
                capabilities = len(agent_info.get('capabilities', []))
                conversations = agent_info.get('conversation_count', 0)
                print(f"• {agent_name}: {capabilities} capabilities, {conversations} conversations")
                print(f"  Description: {agent_info.get('description', 'No description')}")
        else:
            print("\n❌ System not initialized")
    
    async def shutdown(self):
        """Shutdown the application"""
        self.logger.info("Shutting down application...")
        self.running = False
        
        # Shutdown orchestrator
        if self.orchestrator:
            await self.orchestrator.shutdown()
        
        # Cancel MCP server task
        if self.mcp_server_task and not self.mcp_server_task.done():
            self.mcp_server_task.cancel()
            try:
                await self.mcp_server_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Application shutdown complete")


async def main():
    """Main entry point"""
    # Setup logging
    env_vars = load_environment()
    log_level = env_vars.get("LOG_LEVEL", "INFO")
    setup_logging(log_level)
    
    logger = get_logger("Main")
    
    try:
        # Create and initialize application
        app = MultiAgentApp()
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(app.shutdown)
        
        # Initialize application
        await app.initialize()
        
        # Run interactive mode
        await app.run_interactive()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"\n❌ Fatal error: {str(e)}")
        return 1
    finally:
        # Ensure cleanup
        if 'app' in locals():
            await app.shutdown()
    
    return 0


if __name__ == "__main__":
    # Run the application
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
