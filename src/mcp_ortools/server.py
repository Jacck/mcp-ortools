import asyncio
import json
import logging
from typing import Dict, Any, Optional
from .solver import ORToolsSolver, Solution
from .parser import RCPSPParser, RCPSPExpressionBuilder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPServer:
    """MCP Server implementation using OR-Tools"""
    
    def __init__(self):
        self.solver = ORToolsSolver()
        self.parser = RCPSPParser()
        self.builder: Optional[RCPSPExpressionBuilder] = None
        
    async def handle_request(self, data: str) -> str:
        """Handle incoming MCP requests"""
        try:
            request = json.loads(data)
            command = request.get('command')
            
            handlers = {
                'submit_model': self._handle_submit_model,
                'solve_model': self._handle_solve_model,
                'get_solution': self._handle_get_solution,
                'set_parameter': self._handle_set_parameter,
                'get_variable': self._handle_get_variable,
                'get_solve_time': self._handle_get_solve_time,
            }
            
            handler = handlers.get(command)
            if handler:
                response = await handler(request)
            else:
                response = {'status': 'ERROR', 'message': f'Unknown command: {command}'}
                
            return json.dumps(response)
            
        except Exception as e:
            logger.exception("Error handling request")
            return json.dumps({
                'status': 'ERROR',
                'message': str(e)
            })
            
    async def _handle_submit_model(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle model submission"""
        try:
            model_str = request.get('model', '')
            parsed_model = self.parser.parse(model_str)
            
            # Clear previous model
            self.solver.clear()
            
            # Create expression builder with new model
            self.builder = RCPSPExpressionBuilder(self.solver.model)
            
            # Build the model
            variables = self.builder.build_rcpsp_model(
                parsed_model['tasks'],
                parsed_model['resource_capacities']
            )
            
            return {
                'status': 'SUCCESS',
                'message': 'Model submitted successfully'
            }
            
        except Exception as e:
            logger.exception("Error submitting model")
            return {
                'status': 'ERROR',
                'message': f'Error submitting model: {str(e)}'
            }
            
    async def _handle_solve_model(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle model solving"""
        try:
            timeout = request.get('timeout')
            solution = self.solver.solve(timeout)
            
            return {
                'status': 'SUCCESS',
                'solution': {
                    'variables': solution.variables,
                    'status': solution.status,
                    'solve_time': solution.solve_time,
                    'objective_value': solution.objective_value
                }
            }
            
        except Exception as e:
            logger.exception("Error solving model")
            return {
                'status': 'ERROR',
                'message': f'Error solving model: {str(e)}'
            }
            
    async def _handle_get_solution(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle solution retrieval"""
        if not self.solver.last_solution:
            return {
                'status': 'ERROR',
                'message': 'No solution available'
            }
            
        return {
            'status': 'SUCCESS',
            'solution': {
                'variables': self.solver.last_solution.variables,
                'status': self.solver.last_solution.status,
                'solve_time': self.solver.last_solution.solve_time,
                'objective_value': self.solver.last_solution.objective_value
            }
        }
        
    async def _handle_set_parameter(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle parameter setting"""
        try:
            name = request.get('name')
            value = request.get('value')
            
            if not name:
                return {
                    'status': 'ERROR',
                    'message': 'Parameter name is required'
                }
                
            if value is None:
                return {
                    'status': 'ERROR',
                    'message': 'Parameter value is required'
                }
                
            self.solver.parameters[name] = value
            return {
                'status': 'SUCCESS',
                'message': f'Parameter {name} set to {value}'
            }
            
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': f'Error setting parameter: {str(e)}'
            }
            
    async def _handle_get_variable(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle variable value retrieval"""
        name = request.get('name')
        if not self.solver.last_solution or name not in self.solver.last_solution.variables:
            return {
                'status': 'ERROR',
                'message': f'Variable {name} not found in solution'
            }
            
        return {
            'status': 'SUCCESS',
            'value': self.solver.last_solution.variables[name]
        }
        
    async def _handle_get_solve_time(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle solve time retrieval"""
        if not self.solver.last_solution:
            return {
                'status': 'ERROR',
                'message': 'No solution available'
            }
            
        return {
            'status': 'SUCCESS',
            'solve_time': self.solver.last_solution.solve_time
        }

async def handle_stdin_stdout():
    """Handle MCP protocol communication via stdin/stdout"""
    server = MCPServer()
    
    while True:
        try:
            # Read length
            length_str = await asyncio.get_event_loop().run_in_executor(
                None, input
            )
            length = int(length_str)
            
            # Read data
            data = await asyncio.get_event_loop().run_in_executor(
                None, lambda: input()
            )
            
            # Process request
            response = await server.handle_request(data)
            
            # Write response
            print(len(response))
            print(response)
            
        except EOFError:
            break
        except Exception as e:
            logger.exception("Error in main loop")
            response = json.dumps({
                'status': 'ERROR',
                'message': str(e)
            })
            print(len(response))
            print(response)

def main():
    """Main entry point"""
    asyncio.run(handle_stdin_stdout())