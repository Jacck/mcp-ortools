from ortools.sat.python import cp_model
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
import time

@dataclass
class Solution:
    """Represents a solution from the solver"""
    variables: Dict[str, Any]
    status: str
    solve_time: float
    objective_value: Optional[float] = None

class SolutionCallback(cp_model.CpSolverSolutionCallback):
    """Callback to handle solutions during solving"""
    def __init__(self, variables: Dict[str, cp_model.IntVar]):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables = variables
        self.solutions: List[Dict[str, Any]] = []

    def on_solution_callback(self) -> None:
        solution = {
            name: self.Value(var)
            for name, var in self.__variables.items()
        }
        self.solutions.append(solution)

class ORToolsSolver:
    """Main solver class using OR-Tools"""
    def __init__(self):
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        self.variables: Dict[str, cp_model.IntVar] = {}
        self.parameters: Dict[str, Any] = {}
        self.last_solution: Optional[Solution] = None
        self._objective = None

    def create_variable(self, name: str, domain: tuple[int, int]) -> cp_model.IntVar:
        """Create a new integer variable"""
        var = self.model.NewIntVar(domain[0], domain[1], name)
        self.variables[name] = var
        return var

    def create_bool_variable(self, name: str) -> cp_model.IntVar:
        """Create a new boolean variable"""
        var = self.model.NewBoolVar(name)
        self.variables[name] = var
        return var

    def add_constraint(self, constraint: cp_model.Constraint) -> None:
        """Add a constraint to the model"""
        self.model.Add(constraint)

    def set_objective(self, objective: Union[cp_model.LinearExpr, cp_model.IntVar], maximize: bool = True) -> None:
        """Set the optimization objective"""
        self._objective = objective
        if maximize:
            self.model.Maximize(objective)
        else:
            self.model.Minimize(objective)

    def solve(self, timeout: Optional[int] = None) -> Solution:
        """Solve the model with the given timeout"""
        if timeout:
            self.solver.parameters.max_time_in_seconds = timeout

        start_time = time.time()
        callback = SolutionCallback(self.variables)
        status = self.solver.Solve(self.model, callback)
        solve_time = time.time() - start_time

        status_map = {
            cp_model.OPTIMAL: "OPTIMAL",
            cp_model.FEASIBLE: "FEASIBLE",
            cp_model.INFEASIBLE: "INFEASIBLE",
            cp_model.UNKNOWN: "UNKNOWN",
            cp_model.MODEL_INVALID: "INVALID"
        }

        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE] and callback.solutions:
            variables = callback.solutions[-1]
            objective_value = self.solver.ObjectiveValue() if self._objective is not None else None
        else:
            variables = {}
            objective_value = None

        self.last_solution = Solution(
            variables=variables,
            status=status_map.get(status, "UNKNOWN"),
            solve_time=solve_time,
            objective_value=objective_value
        )
        return self.last_solution

    def clear(self) -> None:
        """Clear the current model and variables"""
        self.model = cp_model.CpModel()
        self.variables.clear()
        self.parameters.clear()
        self.last_solution = None
        self._objective = None