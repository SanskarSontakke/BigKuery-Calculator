import sys
sys.path.insert(0, '/home/sanskarsontakke/Documents/antigravity/bold-darwin/BigKuery-Calculator')

import sympy
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, function_exponentiation, convert_xor
from bigkuery.core.solver import get_sympy_dicts, sympy_to_html

transformations = standard_transformations + (implicit_multiplication_application, function_exponentiation, convert_xor)
eval_dict, display_dict = get_sympy_dicts(deg_mode=True)

def substitute_unevaluated(expr, target, replacement):
    if expr == target:
        return replacement
    if expr.is_Atom:
        return expr
    new_args = [substitute_unevaluated(arg, target, replacement) for arg in expr.args]
    try:
        return expr.func(*new_args, evaluate=False)
    except Exception:
        return expr.func(*new_args)

def find_reducible(expr, eval_dict):
    if expr.is_Atom:
        return None
    for arg in expr.args:
        res = find_reducible(arg, eval_dict)
        if res is not None:
            return res
            
    func_name = expr.func.__name__.lower()
    # Check if we should use eval_dict (only if it has no free symbols)
    if func_name in eval_dict and not expr.free_symbols:
        func = eval_dict[func_name]
        try:
            val = func(*expr.args)
            if val != expr:
                return expr
        except Exception:
            pass
    else:
        try:
            val = expr.func(*expr.args)
            if val != expr:
                return expr
        except Exception:
            pass
    return None

def evaluate_node(expr, eval_dict):
    func_name = expr.func.__name__.lower()
    if func_name in eval_dict and not expr.free_symbols:
        func = eval_dict[func_name]
        return func(*expr.args)
    return expr.func(*expr.args)

def solve_workspace_expression_steps(expr_str, definitions, deg_mode=True):
    processed = expr_str.replace('×', '*').replace('÷', '/').replace('−', '-')
    
    expr = parse_expr(processed, local_dict=display_dict, transformations=transformations, evaluate=False)
    
    curr = expr
    for var_name, var_val in definitions.items():
        curr = substitute_unevaluated(curr, sympy.Symbol(var_name), var_val)
        
    steps = [expr]
    if curr != expr:
        steps.append(curr)
        
    while True:
        target = find_reducible(curr, eval_dict)
        if target is None:
            break
        target_eval = evaluate_node(target, eval_dict)
        curr = substitute_unevaluated(curr, target, target_eval)
        if any(str(step) == str(curr) for step in steps):
            break
        steps.append(curr)
        
    html_lines = []
    seen = set()
    for step in steps:
        html = sympy_to_html(step, deg_mode)
        if html not in seen:
            html_lines.append(html)
            seen.add(html)
            
    if not curr.is_number:
        simplified = sympy.simplify(curr)
        if simplified != curr:
            html = sympy_to_html(simplified, deg_mode)
            if html not in seen:
                html_lines.append(f"= {html}")
        elif len(html_lines) == 1:
            html_lines.append(f"= {html_lines[0]}")
        else:
            html_lines[-1] = f"= {html_lines[-1]}"
        return html_lines, {}
        
    val = curr.evalf()
    if val.is_real:
        approx_val = float(val)
        if abs(approx_val) < 1e-4 or abs(approx_val) > 1e6:
            s = f"{approx_val:.12e}"
            if 'e' in s:
                base, exp = s.split('e')
                exp = int(exp)
                approx_line = f"≈ {base} &times; 10<sup>{exp}</sup>"
            else:
                approx_line = f"≈ {approx_val:.12g}"
        else:
            approx_line = f"≈ {approx_val:.12g}"
    else:
        approx_line = f"≈ {val:.12g}"
        
    if approx_line not in seen:
        html_lines.append(approx_line)
        
    return html_lines, {}

print('9 - (3 + 3):', solve_workspace_expression_steps('9 - (3 + 3)', {}))
print('sin(x)^2/sin(x):', solve_workspace_expression_steps('sin(x)^2/sin(x)', {}))
print('x + 2 (x=3):', solve_workspace_expression_steps('x + 2', {'x': 3}))
print('sin(x):', solve_workspace_expression_steps('sin(x)', {}))
