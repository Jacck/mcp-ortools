from typing import Dict, Any, Tuple, Optional, List, Set
from ortools.sat.python import cp_model
import re
import json

class RCPSPParser:
    """Parser for RCPSP models"""
    
    def __init__(self):
        self.tasks: List[Dict[str, Any]] = []
        self.resource_capacities: List[int] = []
        
    def parse(self, model_str: str) -> Dict[str, Any]:
        """Parse RCPSP model string into components"""
        try:
            data = json.loads(model_str)
            self.tasks = data.get('tasks', [])
            self.resource_capacities = data.get('resource_capacities', [])
            
            return {
                'tasks': self.tasks,
                'resource_capacities': self.resource_capacities
            }
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")

class RCPSPExpressionBuilder:
    """Builds OR-Tools CP-SAT model for RCPSP"""
    
    def __init__(self, model: cp_model.CpModel):
        self.model = model
        self.variables: Dict[str, Any] = {}
        
    def build_rcpsp_model(self, tasks: List[Dict[str, Any]], resource_capacities: List[int]) -> Dict[str, Any]:
        """Build complete RCPSP model"""
        num_tasks = len(tasks)
        horizon = sum(task['duration'] for task in tasks)
        
        # Create variables
        task_starts = [
            self.model.NewIntVar(0, horizon, f'task{i}_start') 
            for i in range(num_tasks)
        ]
        task_ends = [
            self.model.NewIntVar(0, horizon, f'task{i}_end')
            for i in range(num_tasks)
        ]
        
        # Create interval variables
        task_intervals = [
            self.model.NewIntervalVar(
                task_starts[i],
                tasks[i]['duration'],
                task_ends[i],
                f'interval{i}'
            )
            for i in range(num_tasks)
        ]
        
        # Add precedence constraints
        for i, task in enumerate(tasks):
            for pred in task['predecessors']:
                self.model.Add(task_ends[pred] <= task_starts[i])
        
        # Add resource constraints
        for res_id, capacity in enumerate(resource_capacities):
            self.model.AddCumulative(
                task_intervals,
                [task['resources'][res_id] for task in tasks],
                capacity
            )
        
        # Store variables for solution extraction
        self.variables = {
            'task_starts': task_starts,
            'task_ends': task_ends,
            'task_intervals': task_intervals,
            'makespan': task_ends[-1]  # Project completion time
        }
        
        # Set objective to minimize makespan
        self.model.Minimize(task_ends[-1])
        
        return self.variables