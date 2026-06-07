import sympy
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, function_exponentiation, convert_xor
from bigkuery.core.solver import get_sympy_dicts, substitute_unevaluated, find_reducible, evaluate_node, sympy_to_html

transformations = standard_transformations + (implicit_multiplication_application, function_exponentiation, convert_xor)
processed = "sin(x)"
definitions = {'x': 30.0}
deg_mode = True

print("1. get_sympy_dicts")
eval_dict, display_dict = get_sympy_dicts(deg_mode)

print("2. parse_expr")
expr = parse_expr(processed, local_dict=display_dict, transformations=transformations, evaluate=False)
print("Parsed expr:", expr, type(expr))

print("3. substitute_unevaluated")
curr = expr
for var_name, var_val in definitions.items():
    print(f"substituting {var_name} with {var_val}...")
    curr = substitute_unevaluated(curr, sympy.Symbol(var_name), var_val)
print("Substituted curr:", curr, type(curr))

steps = [expr]
if curr != expr:
    steps.append(curr)

print("4. reduce step by step loop")
iter_cnt = 0
while True:
    iter_cnt += 1
    print(f"Iteration {iter_cnt} start")
    print("calling find_reducible...")
    target = find_reducible(curr, eval_dict)
    print("find_reducible returned:", target)
    if target is None:
        print("target is None, breaking")
        break
    print("calling evaluate_node...")
    target_eval = evaluate_node(target, eval_dict)
    print("evaluate_node returned:", target_eval)
    print("calling substitute_unevaluated...")
    curr = substitute_unevaluated(curr, target, target_eval)
    print("substitute_unevaluated returned:", curr)
    if any(str(step) == str(curr) for step in steps):
        print("curr already in steps, breaking")
        break
    steps.append(curr)

print("5. convert steps to HTML")
html_lines = []
seen = set()
for step in steps:
    print("converting step to HTML:", step)
    html = sympy_to_html(step, deg_mode)
    print("HTML:", html)
    if html not in seen:
        html_lines.append(html)
        seen.add(html)

print("6. handle symbolic/numeric result")
if not curr.is_number:
    print("is NOT number")
else:
    print("is number, evaluating evalf...")
    val = curr.evalf()
    print("evalf returned:", val)
    approx_val = float(val)
    approx_line = f"≈ {approx_val:.12g}"
    if approx_line not in seen:
        html_lines.append(approx_line)

print("Done! html_lines:", html_lines)
