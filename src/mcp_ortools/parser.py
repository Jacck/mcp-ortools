from typing import Dict, Any, Tuple, Optional, List
from ortools.sat.python import cp_model
import json

class ModelParser:
    def __init__(self):
        self.model = cp_model.CpModel()
        self.variables = {}
        
    def parse(self, model_str: str) -> Tuple[cp_model.CpModel, Dict[str, cp_model.IntVar]]:
        try:
            data = json.loads(model_str)
            
            # Create variables
            for var in data.get('variables', []):
                name = var['name']
                domain = var.get('domain', [0, 1])
                self.variables[name] = self.model.NewIntVar(domain[0], domain[1], name)
            
            # Add constraints
            for constraint in data.get('constraints', []):
                if '<=' in constraint:
                    left, right = constraint.split('<=')
                    self.model.Add(self._parse_expr(left) <= self._parse_expr(right))
                elif '>=' in constraint:
                    left, right = constraint.split('>=')
                    self.model.Add(self._parse_expr(left) >= self._parse_expr(right))
                elif '!=' in constraint:
                    left, right = constraint.split('!=')
                    self.model.Add(self._parse_expr(left) != self._parse_expr(right))
                elif '==' in constraint:
                    left, right = constraint.split('==')
                    self.model.Add(self._parse_expr(left) == self._parse_expr(right))
            
            # Handle objective if present
            objective = data.get('objective')
            if objective:
                expr = objective.get('expression')
                maximize = objective.get('maximize', True)
                if maximize:
                    self.model.Maximize(self._parse_expr(expr))
                else:
                    self.model.Minimize(self._parse_expr(expr))
            
            return self.model, self.variables
            
        except Exception as e:
            raise ValueError(f"Error parsing model: {str(e)}")
    
    def _parse_expr(self, expr_str: str) -> cp_model.LinearExpr:
        expr_str = expr_str.strip()
        
        # Try parsing as integer
        try:
            return int(expr_str)
        except ValueError:
            pass
            
        # Check if it's a simple variable reference
        if expr_str in self.variables:
            return self.variables[expr_str]
            
        # Handle arithmetic expressions
        if '+' in expr_str:
            left, right = expr_str.split('+', 1)
            return self._parse_expr(left) + self._parse_expr(right)
        elif '-' in expr_str and not expr_str.startswith('-'):
            left, right = expr_str.split('-', 1)
            return self._parse_expr(left) - self._parse_expr(right)
        elif expr_str.startswith('-'):
            return -self._parse_expr(expr_str[1:])
        elif '*' in expr_str:
            coeff, var = expr_str.split('*', 1)
            return int(coeff.strip()) * self._parse_expr(var)
            
        raise ValueError(f"Unable to parse expression: {expr_str}")
