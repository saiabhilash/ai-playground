"""
Web API version of the multi-agent system
Runs as a service with REST endpoints
"""
import asyncio
import sys
import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.logger import setup_logging, get_logger
from core.orchestrator import AgentOrchestrator
from mcp_server.server import start_mcp_server
from utils.helpers import load_environment, validate_environment, wait_for_mcp_server

# FastAPI app
app = FastAPI(
    title="Simple Multi-Agent System API",
    description="REST API for the multi-agent system with MCP server",
    version="1.0.0"
)

# Global variables
orchestrator: Optional[AgentOrchestrator] = None
mcp_server_task: Optional[asyncio.Task] = None
logger = get_logger("WebAPI")

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    agent: str
    success: bool

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Simple Multi-Agent System",
        "status": "running",
        "version": "1.0.0",
        "agents": ["MathAgent", "TextAgent", "TaskAgent"],
        "endpoints": {
            "chat": "/chat",
            "status": "/status",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if orchestrator and orchestrator.agents:
        return {"status": "healthy", "agents": len(orchestrator.agents)}
    return {"status": "initializing"}

@app.get("/status")
async def get_status():
    """Get system status"""
    if not orchestrator:
        return {"status": "not_initialized"}
    
    status = orchestrator.get_system_status()
    return {
        "status": "running",
        "agents": list(status['agents'].keys()),
        "conversation_turns": status.get('conversation_turns', 0),
        "agent_details": status['agents']
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with the multi-agent system"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        logger.info(f"Processing message: {request.message}")
        response = await orchestrator.process_message(request.message)
        
        return ChatResponse(
            response=response.content,
            agent=response.agent,
            success=True
        )
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
async def startup_event():
    """Initialize the system on startup"""
    global orchestrator, mcp_server_task
    
    setup_logging("INFO")
    logger.info("Starting Multi-Agent System API...")
    
    try:
        # Load configuration
        env_vars = load_environment()
        if not validate_environment(env_vars):
            raise Exception("Environment validation failed")
        
        # Start MCP server on different port to avoid conflicts
        mcp_host = "localhost"
        mcp_port = 8001
        mcp_url = f"http://{mcp_host}:{mcp_port}"
        
        logger.info(f"Starting MCP server on {mcp_host}:{mcp_port}")
        mcp_server_task = asyncio.create_task(
            start_mcp_server(mcp_host, mcp_port)
        )
        
        # Wait for MCP server
        if not await wait_for_mcp_server(mcp_host, mcp_port, max_attempts=10):
            raise Exception("MCP server failed to start")
        
        # Initialize orchestrator
        logger.info("Initializing orchestrator...")
        orchestrator = AgentOrchestrator(mcp_url)
        await orchestrator.initialize()
        
        logger.info("Multi-Agent System API ready!")
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global orchestrator, mcp_server_task
    
    logger.info("Shutting down Multi-Agent System API...")
    
    if orchestrator:
        await orchestrator.shutdown()
    
    if mcp_server_task and not mcp_server_task.done():
        mcp_server_task.cancel()
        try:
            await mcp_server_task
        except asyncio.CancelledError:
            pass
    
    logger.info("Shutdown complete")

if __name__ == "__main__":
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )
