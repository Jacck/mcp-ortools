# MCP-ORTools

A Model Context Protocol (MCP) server implementation using Google OR-Tools for constraint solving.

## Overview

MCP-ORTools integrates Google's OR-Tools constraint programming solver with Large Language Models through the Model Context Protocol, enabling AI models to:
- Submit and validate constraint models
- Set model parameters
- Solve constraint satisfaction and optimization problems
- Retrieve and analyze solutions
- Handle Resource-Constrained Project Scheduling Problems (RCPSP)

## Installation

1. Install the package:
```bash
pip install git+https://github.com/Jacck/mcp-ortools.git
```

2. Configure Claude Desktop:
Create a configuration file at `~/Library/Application/Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):
```json
{
  "mcpServers": {
    "ortools": {
      "command": "mcp-ortools"
    }
  }
}
```

## Usage

### Simple Optimization Problem
```json
{
    "variables": [
        {"name": "x", "domain": [0, 10]},
        {"name": "y", "domain": [0, 10]}
    ],
    "constraints": [
        "x + y <= 15",
        "x >= 2 * y"
    ],
    "objective": {
        "expression": "40 * x + 100 * y",
        "maximize": true
    }
}
```

### RCPSP Problem
```json
{
    "tasks": [
        {"id": 0, "duration": 0, "predecessors": [], "resources": [0, 0]},
        {"id": 1, "duration": 6, "predecessors": [0], "resources": [2, 1]},
        {"id": 2, "duration": 1, "predecessors": [0], "resources": [1, 0]}
    ],
    "resource_capacities": [7, 4]
}
```

## License

MIT License - see LICENSE file for details.