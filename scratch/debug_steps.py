import sympy
from bigkuery.core.solver import solve_workspace_expression_steps

print("Calling solve_workspace_expression_steps...")
res, defs = solve_workspace_expression_steps("sin(x)", {'x': 30.0}, deg_mode=True)
print("Finished successfully!")
print("Result:", res)
