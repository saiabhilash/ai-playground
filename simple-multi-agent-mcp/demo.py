"""
Demonstration script for the Simple Multi-Agent System
Shows automated interactions with the system
"""
import asyncio
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.logger import setup_logging, get_logger
from core.orchestrator import AgentOrchestrator
from mcp_server.server import start_mcp_server
from utils.helpers import wait_for_mcp_server, format_response


async def run_demo():
    """Run demonstration of the multi-agent system"""
    
    # Setup logging
    setup_logging("INFO")
    logger = get_logger("Demo")
    
    print("🚀 Starting Simple Multi-Agent System Demo\n")
    
    try:
        # Configuration
        mcp_host = "localhost"
        mcp_port = 8001  # Use different port for demo
        mcp_url = f"http://{mcp_host}:{mcp_port}"
        
        # Start MCP server
        logger.info(f"Starting MCP server on {mcp_host}:{mcp_port}")
        mcp_server_task = asyncio.create_task(
            start_mcp_server(mcp_host, mcp_port)
        )
        
        # Wait for MCP server to be ready
        print("⏳ Waiting for MCP server to start...")
        if not await wait_for_mcp_server(mcp_host, mcp_port, max_attempts=10):
            raise Exception("MCP server failed to start")
        
        print("✅ MCP server is ready\n")
        
        # Initialize orchestrator
        print("🤖 Initializing agents...")
        orchestrator = AgentOrchestrator(mcp_url)
        await orchestrator.initialize()
        
        print(f"✅ Initialized {len(orchestrator.agents)} agents\n")
        
        # Demo scenarios
        demo_messages = [
            "Calculate the sum of 15 and 27",
            "Solve the equation 2x + 5 = 15",
            "Analyze the sentiment of this text: 'I love sunny days and beautiful weather!'",
            "Count the words in this sentence: 'The quick brown fox jumps over the lazy dog'",
            "What's the square root of 144?",
            "Extract numbers from this text: 'I have 5 apples, 3 oranges, and 12 bananas'",
            "Help me plan a task to calculate 10 * 5 and then analyze the result"
        ]
        
        print("🎯 **Demo Scenarios**\n")
        
        for i, message in enumerate(demo_messages, 1):
            print(f"**Scenario {i}:**")
            print(f"👤 User: {message}")
            
            # Process message
            response = await orchestrator.process_message(message)
            
            # Display response
            print(f"🤖 {format_response(response)}")
            print("-" * 80)
            
            # Small delay between scenarios
            await asyncio.sleep(1)
        
        # Show system status
        print("\n📊 **Final System Status:**")
        status = orchestrator.get_system_status()
        print(f"• Total conversation turns: {status['conversation_turns']}")
        print(f"• Agents used: {list(status['agents'].keys())}")
        
        for agent_name, agent_info in status['agents'].items():
            conversations = agent_info.get('conversation_count', 0)
            print(f"  - {agent_name}: {conversations} conversations")
        
        print("\n✅ Demo completed successfully!")
        
        # Cleanup
        await orchestrator.shutdown()
        
        if not mcp_server_task.done():
            mcp_server_task.cancel()
            try:
                await mcp_server_task
            except asyncio.CancelledError:
                pass
                
    except Exception as e:
        logger.error(f"Demo error: {e}")
        print(f"\n❌ Demo failed: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    print("Simple Multi-Agent System - Demo Mode")
    print("=" * 50)
    
    exit_code = asyncio.run(run_demo())
    
    print("\n" + "=" * 50)
    print("Demo finished. Run 'python main.py' for interactive mode.")
    
    sys.exit(exit_code)
