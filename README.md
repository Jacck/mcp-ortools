# MCP-ORTools

A Model Context Protocol (MCP) server implementation using Google OR-Tools for constraint solving. Designed for use with Large Language Models through standardized constraint model specification.

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

## Model Specification

Models are specified in JSON format with three main sections:
- `variables`: Define variables and their domains
- `constraints`: List of constraints using OR-Tools methods
- `objective`: Optional optimization objective

### Constraint Syntax

Constraints must use OR-Tools method syntax:
- `.__le__()` for less than or equal (<=)
- `.__ge__()` for greater than or equal (>=)
- `.__eq__()` for equality (==)
- `.__ne__()` for not equal (!=)

## Usage Examples

### Simple Optimization Model
```json
{
    "variables": [
        {"name": "x", "domain": [0, 10]},
        {"name": "y", "domain": [0, 10]}
    ],
    "constraints": [
        "(x + y).__le__(15)",
        "x.__ge__(2 * y)"
    ],
    "objective": {
        "expression": "40 * x + 100 * y",
        "maximize": true
    }
}
```

### Knapsack Problem
Example: Select items with values [3,1,2,1] and weights [2,2,1,1] with total weight limit of 2.

```json
{
    "variables": [
        {"name": "p0", "domain": [0, 1]},
        {"name": "p1", "domain": [0, 1]},
        {"name": "p2", "domain": [0, 1]},
        {"name": "p3", "domain": [0, 1]}
    ],
    "constraints": [
        "(2*p0 + 2*p1 + p2 + p3).__le__(2)"
    ],
    "objective": {
        "expression": "3*p0 + p1 + 2*p2 + p3",
        "maximize": true
    }
}
```

Additional constraints example:
```json
{
    "constraints": [
        "p0.__eq__(1)",         // Item p0 must be selected
        "p1.__ne__(p2)",        // Can't select both p1 and p2
        "(p2 + p3).__ge__(1)"   // Must select at least one of p2 or p3
    ]
}
```

## Features

- Full OR-Tools CP-SAT solver support
- JSON-based model specification
- Support for:
  - Integer and boolean variables (domain: [min, max])
  - Linear constraints using OR-Tools method syntax
  - Linear optimization objectives
  - Timeouts and solver parameters
  - Binary constraints and relationships
  - Portfolio selection problems
  - Knapsack problems

### Supported Operations in Constraints
- Basic arithmetic: +, -, *
- Comparisons: .__le__(), .__ge__(), .__eq__(), .__ne__()
- Linear combinations of variables
- Binary logic through combinations of constraints

## Development

To setup for development:
```bash
git clone https://github.com/Jacck/mcp-ortools.git
cd mcp-ortools
pip install -e .
```

## Model Response Format

The solver returns solutions in JSON format:
```json
{
    "status": "OPTIMAL",
    "solve_time": 0.045,
    "variables": {
        "p0": 0,
        "p1": 0,
        "p2": 1,
        "p3": 1
    },
    "objective_value": 3.0
}
```

Status values:
- OPTIMAL: Found optimal solution
- FEASIBLE: Found feasible solution
- INFEASIBLE: No solution exists
- UNKNOWN: Could not determine solution

## License

MIT License - see LICENSE file for details
