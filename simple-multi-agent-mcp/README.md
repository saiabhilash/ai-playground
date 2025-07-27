# Simple Multi-Agent Solution with MCP Server

This is a simplified multi-agent system using Python and Model Context Protocol (MCP) server that demonstrates basic agent coordination for simple tasks.

## Overview

This solution creates a simple multi-agent system with:
- **Task Agent**: Handles task planning and coordination
- **Math Agent**: Performs mathematical calculations
- **Text Agent**: Handles text processing and analysis
- **MCP Server**: Provides context and tool integration

## Features

- Simple agent orchestration
- MCP server integration for tool and context management
- Basic task delegation between agents
- Interactive chat interface
- Logging and monitoring

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Task Agent    │    │   Math Agent     │    │   Text Agent    │
│  (Coordinator)  │◄──►│  (Calculator)    │    │  (Processor)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                         ┌───────▼──────┐
                         │  MCP Server  │
                         │   (Tools &   │
                         │   Context)   │
                         └──────────────┘
```

## Requirements

- Python 3.11+
- Dependencies listed in requirements.txt

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Run the application:
   ```bash
   python main.py
   ```

## Usage

The system can handle simple tasks like:
- Mathematical calculations
- Text analysis
- Task coordination
- Basic problem solving

Example interactions:
- "Calculate the sum of 15 and 27"
- "Analyze the sentiment of this text: 'I love sunny days'"
- "Plan a task to solve 2x + 5 = 15 and explain the result"

## Project Structure

```
simple-multi-agent-mcp/
├── main.py              # Main application entry point
├── requirements.txt     # Python dependencies
├── .env.example        # Environment variables template
├── mcp_server/         # MCP server implementation
│   ├── __init__.py
│   ├── server.py       # MCP server core
│   └── tools.py        # Available tools
├── agents/             # Agent implementations
│   ├── __init__.py
│   ├── base_agent.py   # Base agent class
│   ├── task_agent.py   # Task coordination agent
│   ├── math_agent.py   # Mathematical operations agent
│   └── text_agent.py   # Text processing agent
├── core/               # Core system components
│   ├── __init__.py
│   ├── orchestrator.py # Agent orchestration
│   └── logger.py       # Logging configuration
└── utils/              # Utility functions
    ├── __init__.py
    └── helpers.py      # Helper functions
```
