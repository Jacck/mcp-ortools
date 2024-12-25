from typing import Dict, Any, Tuple, Optional, List, Set
from ortools.sat.python import cp_model
import re
import json

class ModelParser:
    """Parser for generic optimization models"""
    
    def __init__(self):
        self.variables: Dict[str, Tuple[int, int]] = {}
        self.constraints: List[str] = []
        self.objective: Optional[Tuple[str, bool]] = None  # (expr, is_maximize)
        
    def parse(self, model_str: str) -> Dict[str, Any]:
        """Parse model string into components"""
        try:
            data = json.loads(model_str)
            
            # Parse variables
            for var in data.get('variables', []):
                name = var['name']
                domain = tuple(var['domain'])
                self.variables[name] = domain
            
            # Parse constraints
            self.constraints = data.get('constraints', [])
            
            # Parse objective
            obj = data.get('objective')
            if obj:
                self.objective = (obj['expression'], obj.get('maximize', True))
            
            return {
                'variables': self.variables,
                'constraints': self.constraints,
                'objective': self.objective
            }
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")

class ExpressionBuilder:
    """Builds OR-Tools expressions from parsed strings"""
    
    def __init__(self, variables: Dict[str, cp_model.IntVar]):
        self.variables = variables
        
    def build_constraint(self, expr: str) -> cp_model.Constraint:
        """Convert a constraint string to an OR-Tools constraint"""
        # Split expression into left and right parts
        parts = []
        if '<=' in expr:
            parts = expr.split('<=')
            op = '<='
        elif '>=' in expr:
            parts = expr.split('>=')
            op = '>='
        elif '==' in expr:
            parts = expr.split('==')
            op = '=='
        elif '!=' in expr:
            parts = expr.split('!=')
            op = '!='
        elif '<' in expr:
            parts = expr.split('<')
            op = '<'
        elif '>' in expr:
            parts = expr.split('>')
            op = '>'
        else:
            raise ValueError(f"No valid operator found in: {expr}")
            
        if len(parts) != 2:
            raise ValueError(f"Invalid constraint format: {expr}")
            
        left, right = parts
        
        # Build left and right expressions
        def build_expr(expr_str: str) -> cp_model.LinearExpr:
            # Replace variable names with their OR-Tools variables
            for var_name in sorted(self.variables.keys(), key=len, reverse=True):
                expr_str = expr_str.replace(var_name, f"self.variables['{var_name}']")
            return eval(expr_str)
        
        left_expr = build_expr(left.strip())
        right_expr = build_expr(right.strip())
        
        # Create constraint
        if op == '<=':
            return left_expr <= right_expr
        elif op == '>=':
            return left_expr >= right_expr
        elif op == '==':
            return left_expr == right_expr
        elif op == '!=':
            return left_expr != right_expr
        elif op == '<':
            return left_expr < right_expr
        else:  # op == '>'
            return left_expr > right_expr
        
    def build_objective(self, expr: str) -> cp_model.LinearExpr:
        """Convert an objective expression to an OR-Tools linear expression"""
        # Replace variable names with their OR-Tools variables
        for var_name in sorted(self.variables.keys(), key=len, reverse=True):
            expr = expr.replace(var_name, f"self.variables['{var_name}']")
        return eval(expr)