"""
MCP Server Implementation
Provides tools and context management for the multi-agent system
"""
import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from .tools import get_all_tools, get_tool


class ToolRequest(BaseModel):
    """Tool execution request model"""
    tool_name: str
    method_name: str
    parameters: Dict[str, Any] = {}


class ToolResponse(BaseModel):
    """Tool execution response model"""
    success: bool
    result: Any = None
    error: Optional[str] = None


class ContextRequest(BaseModel):
    """Context retrieval request model"""
    context_type: str
    parameters: Dict[str, Any] = {}


class MCPServer:
    """Model Context Protocol Server for tool and context management"""
    
    def __init__(self, host: str = "localhost", port: int = 8000):
        self.host = host
        self.port = port
        self.app = FastAPI(title="MCP Server", description="Model Context Protocol Server")
        self.tools = get_all_tools()
        self.logger = logging.getLogger(__name__)
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/")
        async def root():
            return {"message": "MCP Server is running", "tools": list(self.tools.keys())}
        
        @self.app.get("/tools")
        async def list_tools():
            """List all available tools"""
            tool_info = {}
            for tool_name, tool_instance in self.tools.items():
                methods = [method for method in dir(tool_instance) 
                          if not method.startswith('_') and callable(getattr(tool_instance, method))]
                tool_info[tool_name] = {
                    "methods": methods,
                    "description": tool_instance.__class__.__doc__ or "No description available"
                }
            return {"tools": tool_info}
        
        @self.app.post("/execute_tool")
        async def execute_tool(request: ToolRequest) -> ToolResponse:
            """Execute a tool method with given parameters"""
            try:
                tool = get_tool(request.tool_name)
                if not tool:
                    raise HTTPException(status_code=404, detail=f"Tool '{request.tool_name}' not found")
                
                method = getattr(tool, request.method_name, None)
                if not method:
                    raise HTTPException(status_code=404, detail=f"Method '{request.method_name}' not found in tool '{request.tool_name}'")
                
                if not callable(method):
                    raise HTTPException(status_code=400, detail=f"'{request.method_name}' is not a callable method")
                
                # Execute the method with parameters
                if request.parameters:
                    result = method(**request.parameters)
                else:
                    result = method()
                
                self.logger.info(f"Executed {request.tool_name}.{request.method_name} with parameters {request.parameters}")
                
                return ToolResponse(success=True, result=result)
                
            except Exception as e:
                self.logger.error(f"Error executing tool: {str(e)}")
                return ToolResponse(success=False, error=str(e))
        
        @self.app.post("/get_context")
        async def get_context(request: ContextRequest):
            """Get context information based on request type"""
            try:
                context_type = request.context_type
                
                if context_type == "available_tools":
                    return {
                        "context_type": context_type,
                        "data": {
                            "tools": list(self.tools.keys()),
                            "capabilities": {
                                "calculator": ["basic math", "equation solving"],
                                "text": ["analysis", "processing", "sentiment"],
                                "utility": ["time", "validation", "formatting"]
                            }
                        }
                    }
                elif context_type == "tool_help":
                    tool_name = request.parameters.get("tool_name")
                    if tool_name in self.tools:
                        tool = self.tools[tool_name]
                        methods = [method for method in dir(tool) 
                                 if not method.startswith('_') and callable(getattr(tool, method))]
                        return {
                            "context_type": context_type,
                            "data": {
                                "tool_name": tool_name,
                                "methods": methods,
                                "description": tool.__class__.__doc__
                            }
                        }
                    else:
                        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
                
                else:
                    raise HTTPException(status_code=400, detail=f"Unknown context type: {context_type}")
                
            except Exception as e:
                self.logger.error(f"Error getting context: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
    
    async def start(self):
        """Start the MCP server"""
        config = uvicorn.Config(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        self.logger.info(f"Starting MCP Server on {self.host}:{self.port}")
        await server.serve()
    
    def run(self):
        """Run the MCP server (blocking)"""
        uvicorn.run(self.app, host=self.host, port=self.port)


# Singleton instance for easy access
_mcp_server_instance = None


def get_mcp_server(host: str = "localhost", port: int = 8000) -> MCPServer:
    """Get or create MCP server instance"""
    global _mcp_server_instance
    if _mcp_server_instance is None:
        _mcp_server_instance = MCPServer(host, port)
    return _mcp_server_instance


async def start_mcp_server(host: str = "localhost", port: int = 8000):
    """Start MCP server as async task"""
    server = get_mcp_server(host, port)
    await server.start()


if __name__ == "__main__":
    # Run server directly
    server = MCPServer()
    server.run()
