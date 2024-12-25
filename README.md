# MCP-ORTools

A Model Context Protocol (MCP) server implementation using Google OR-Tools for constraint solving.

## Overview

MCP-ORTools integrates Google's OR-Tools constraint programming solver with Large Language Models through the Model Context Protocol, enabling AI models to:
- Submit and validate constraint models
- Set model parameters
- Solve constraint satisfaction and optimization problems
- Retrieve and analyze solutions

## Installation

1. Install the package:
```bash
pip install git+https://github.com/Jacck/mcp-ortools.git
```

2. Configure Claude Desktop
Create the configuration file at `%APPDATA%\Claude\claude_desktop_config.json` (Windows) or `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):
```json
{
  "mcpServers": {
    "ortools": {
      "command": "python",
      "args": ["-m", "mcp_ortools.server"]
    }
  }
}
```

## Usage Example

Submit an optimization model:
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

## Features

- Full OR-Tools CP-SAT solver support
- JSON-based model specification
- Support for:
  - Integer and boolean variables
  - Linear constraints
  - Optimization objectives
  - Timeouts and solver parameters

## Development

To setup for development:
```bash
git clone https://github.com/Jacck/mcp-ortools.git
cd mcp-ortools
pip install -e .
```

## License

MIT License - see LICENSE file for details.