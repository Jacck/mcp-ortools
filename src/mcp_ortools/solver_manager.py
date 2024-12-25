import logging
import time
from typing import Dict, Any, Optional, Union, Tuple
from ortools.sat.python import cp_model
import json

logger = logging.getLogger(__name__)

class SolverError(Exception):
    """Custom exception for solver-related errors"""
    pass

class SolverManager:
    """Manages OR-Tools solver operations and state"""
    
    def __init__(self):
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        self.variables: Dict[str, cp_model.IntVar] = {}
        self.current_solution: Optional[Dict[str, Any]] = None
        self.last_solve_time: Optional[float] = None
        self.objective_value: Optional[float] = None
        self.solution_status: Optional[str] = None
        
    def clear(self) -> None:
        """Clear current model and solution state"""
        self.model = cp_model.CpModel()
        self.variables.clear()
        self.current_solution = None
        self.last_solve_time = None
        self.objective_value = None
        self.solution_status = None
        
    def parse_model(self, model_str: str) -> Tuple[bool, str]:
        """Parse and validate model definition"""
        try:
            data = json.loads(model_str)
            
            # Clear previous state
            self.clear()
            
            # Validate model structure
            if 'variables' not in data:
                return False, "Model must contain 'variables' field"
                
            # Create variables
            for var_def in data.get('variables', []):
                if 'name' not in var_def or 'domain' not in var_def:
                    return False, "Each variable must have 'name' and 'domain'"
                name = var_def['name']
                domain = tuple(var_def['domain'])
                if len(domain) != 2:
                    return False, f"Domain for variable {name} must be [lower, upper]"
                if domain == (0, 1):
                    self.variables[name] = self.model.NewBoolVar(name)
                else:
                    self.variables[name] = self.model.NewIntVar(domain[0], domain[1], name)
            
            # Add constraints
            for constraint_str in data.get('constraints', []):
                try:
                    constraint = self._build_constraint(constraint_str)
                    self.model.Add(constraint)
                except Exception as e:
                    return False, f"Invalid constraint '{constraint_str}': {str(e)}"
            
            # Set objective if present
            objective = data.get('objective')
            if objective:
                if 'expression' not in objective:
                    return False, "Objective must have 'expression' field"
                try:
                    expr = self._build_expression(objective['expression'])
                    if objective.get('maximize', True):
                        self.model.Maximize(expr)
                    else:
                        self.model.Minimize(expr)
                except Exception as e:
                    return False, f"Invalid objective expression: {str(e)}"
            
            return True, "Model parsed successfully"
            
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON format: {str(e)}"
        except Exception as e:
            logger.exception("Error parsing model")
            return False, f"Error parsing model: {str(e)}"
    
    def solve(self, timeout: Optional[float] = None) -> Dict[str, Any]:
        """Solve current model with optional timeout"""
        if not self.variables:
            raise SolverError("No model loaded or model is empty")
            
        try:
            if timeout:
                self.solver.parameters.max_time_in_seconds = timeout
            
            class SolutionCallback(cp_model.CpSolverSolutionCallback):
                def __init__(self):
                    cp_model.CpSolverSolutionCallback.__init__(self)
                    self.solution_found = False
                    
                def on_solution_callback(self):
                    self.solution_found = True
            
            callback = SolutionCallback()
            start_time = time.time()
            status = self.solver.Solve(self.model, callback)
            self.last_solve_time = time.time() - start_time
            
            status_map = {
                cp_model.OPTIMAL: "OPTIMAL",
                cp_model.FEASIBLE: "FEASIBLE",
                cp_model.INFEASIBLE: "INFEASIBLE",
                cp_model.UNKNOWN: "UNKNOWN",
                cp_model.MODEL_INVALID: "INVALID"
            }
            
            self.solution_status = status_map.get(status, "UNKNOWN")
            result = {
                'status': self.solution_status,
                'solve_time': self.last_solve_time
            }
            
            if status in [cp_model.OPTIMAL, cp_model.FEASIBLE] and callback.solution_found:
                self.current_solution = {
                    name: self.solver.Value(var)
                    for name, var in self.variables.items()
                }
                result['variables'] = self.current_solution
                if self.model.HasObjective():
                    self.objective_value = self.solver.ObjectiveValue()
                    result['objective_value'] = self.objective_value
            elif status == cp_model.INFEASIBLE:
                result['message'] = "Problem is infeasible"
            elif not callback.solution_found:
                result['message'] = "No solution found"
                
            return result
            
        except Exception as e:
            logger.exception("Error solving model")
            raise SolverError(f"Error solving model: {str(e)}")
    
    def _build_constraint(self, constraint_str: str) -> cp_model.Constraint:
        """Build OR-Tools constraint from string expression"""
        if not constraint_str:
            raise ValueError("Empty constraint string")
            
        # Replace variable names with their OR-Tools variables
        expr = constraint_str
        for name, var in sorted(self.variables.items(), key=lambda x: len(x[0]), reverse=True):
            expr = expr.replace(name, f"self.variables['{name}']")
        
        # Handle operators
        expr = expr.replace('<=', '.__le__')
        expr = expr.replace('>=', '.__ge__')
        expr = expr.replace('!=', '.__ne__')
        expr = expr.replace('==', '.__eq__')
        expr = expr.replace('<', '.__lt__')
        expr = expr.replace('>', '.__gt__')
        
        try:
            return eval(expr)
        except Exception as e:
            raise ValueError(f"Invalid constraint expression: {str(e)}")
    
    def _build_expression(self, expr_str: str) -> Union[cp_model.LinearExpr, cp_model.IntVar]:
        """Build OR-Tools expression from string"""
        if not expr_str:
            raise ValueError("Empty expression string")
            
        expr = expr_str
        for name, var in sorted(self.variables.items(), key=lambda x: len(x[0]), reverse=True):
            if name not in expr:
                continue
            expr = expr.replace(name, f"self.variables['{name}']")
            
        try:
            return eval(expr)
        except Exception as e:
            raise ValueError(f"Invalid expression: {str(e)}")
    
    def get_current_solution(self) -> Optional[Dict[str, Any]]:
        """Get current solution if available"""
        if self.current_solution is None:
            return None
        return {
            'variables': self.current_solution,
            'status': self.solution_status,
            'solve_time': self.last_solve_time,
            'objective_value': self.objective_value
        }
    
    def get_solve_time(self) -> Optional[float]:
        """Get last solve time"""
        return self.last_solve_time