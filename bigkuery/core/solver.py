"""
SymPy Solver - Equation parsing, solving, and rich HTML rendering.
"""

import sympy
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations,
    implicit_multiplication_application, function_exponentiation,
    convert_xor
)

# Enable implicit multiplication (e.g. 2x -> 2*x) and convert XOR (e.g. 10^5 -> 10**5)
transformations = standard_transformations + (implicit_multiplication_application, function_exponentiation, convert_xor)


class log10(sympy.Function):
    nargs = 1
    
    @classmethod
    def eval(cls, arg):
        if arg.is_number:
            try:
                val = sympy.log(arg, 10)
                if val.is_Rational or val.is_Integer:
                    return val
            except Exception:
                pass
                
    def _eval_evalf(self, prec):
        return sympy.log(self.args[0], 10).evalf(prec)


class log2(sympy.Function):
    nargs = 1
    
    @classmethod
    def eval(cls, arg):
        if arg.is_number:
            try:
                val = sympy.log(arg, 2)
                if val.is_Rational or val.is_Integer:
                    return val
            except Exception:
                pass
                
    def _eval_evalf(self, prec):
        return sympy.log(self.args[0], 2).evalf(prec)


def get_sympy_dicts(deg_mode=True):
    """Get dictionaries for parsing (eval vs display)."""
    base_dict = {
        'pi': sympy.pi,
        'e': sympy.E,
        'phi': sympy.GoldenRatio,
        'tau': 2 * sympy.pi,
        'euler': sympy.EulerGamma,
        'I': sympy.I,
        'i': sympy.I,
        'deg': sympy.Symbol('deg'),
    }
    
    # Eval dict (actually evaluates angles in degrees if deg_mode=True)
    eval_dict = base_dict.copy()
    if deg_mode:
        eval_dict.update({
            'deg': sympy.Integer(1),
            'sin': lambda x, evaluate=None: sympy.sin(x * sympy.pi / 180),
            'cos': lambda x, evaluate=None: sympy.cos(x * sympy.pi / 180),
            'tan': lambda x, evaluate=None: sympy.tan(x * sympy.pi / 180),
            'cot': lambda x, evaluate=None: sympy.cot(x * sympy.pi / 180),
            'sec': lambda x, evaluate=None: sympy.sec(x * sympy.pi / 180),
            'csc': lambda x, evaluate=None: sympy.csc(x * sympy.pi / 180),
            'asin': lambda x, evaluate=None: sympy.asin(x) * 180 / sympy.pi,
            'acos': lambda x, evaluate=None: sympy.acos(x) * 180 / sympy.pi,
            'atan': lambda x, evaluate=None: sympy.atan(x) * 180 / sympy.pi,
            'acot': lambda x, evaluate=None: sympy.acot(x) * 180 / sympy.pi,
            'asec': lambda x, evaluate=None: sympy.asec(x) * 180 / sympy.pi,
            'acsc': lambda x, evaluate=None: sympy.acsc(x) * 180 / sympy.pi,
        })
    else:
        eval_dict.update({
            'deg': sympy.pi / 180,
            'sin': sympy.sin,
            'cos': sympy.cos,
            'tan': sympy.tan,
            'cot': sympy.cot,
            'sec': sympy.sec,
            'csc': sympy.csc,
            'asin': sympy.asin,
            'acos': sympy.acos,
            'atan': sympy.atan,
            'acot': sympy.acot,
            'asec': sympy.asec,
            'acsc': sympy.acsc,
        })
        
    # Add other functions to eval_dict
    eval_dict.update({
        'sinh': sympy.sinh, 'cosh': sympy.cosh, 'tanh': sympy.tanh,
        'coth': sympy.coth, 'sech': sympy.sech, 'csch': sympy.csch,
        'asinh': sympy.asinh, 'acosh': sympy.acosh, 'atanh': sympy.atanh,
        'exp': sympy.exp, 'log': sympy.log, 'ln': sympy.log,
        'log10': log10, 'log2': log2,
        'sqrt': sympy.sqrt, 'cbrt': sympy.cbrt, 'abs': sympy.Abs,
        'floor': sympy.floor, 'ceil': sympy.ceiling, 'factorial': sympy.factorial,
        'gamma': sympy.gamma, 'min': sympy.Min, 'max': sympy.Max,
    })
    
    # Display dict (does not convert degree values, used for pretty 2D rendering)
    display_dict = base_dict.copy()
    display_dict.update({
        'sin': sympy.sin, 'cos': sympy.cos, 'tan': sympy.tan,
        'cot': sympy.cot, 'sec': sympy.sec, 'csc': sympy.csc,
        'asin': sympy.asin, 'acos': sympy.acos, 'atan': sympy.atan,
        'acot': sympy.acot, 'asec': sympy.asec, 'acsc': sympy.acsc,
        'sinh': sympy.sinh, 'cosh': sympy.cosh, 'tanh': sympy.tanh,
        'coth': sympy.coth, 'sech': sympy.sech, 'csch': sympy.csch,
        'asinh': sympy.asinh, 'acosh': sympy.acosh, 'atanh': sympy.atanh,
        'exp': sympy.exp, 'log': sympy.log, 'ln': sympy.log,
        'log10': log10, 'log2': log2,
        'sqrt': sympy.sqrt, 'cbrt': sympy.cbrt, 'abs': sympy.Abs,
        'floor': sympy.floor, 'ceil': sympy.ceiling, 'factorial': sympy.factorial,
        'gamma': sympy.gamma, 'min': sympy.Min, 'max': sympy.Max,
    })
    
    return eval_dict, display_dict


def sympy_to_html(expr, deg_mode=True, is_trig_arg=False):
    """Recursively render a SymPy expression to standard 2D HTML formatting."""
    if expr is None:
        return ""
        
    if isinstance(expr, str):
        return expr
        
    # Handle singletons / constants cleanly, checking by value, identity, and class name
    if expr == sympy.pi or (hasattr(expr, 'name') and expr.name == 'pi') or expr.__class__.__name__ == 'Pi':
        if is_trig_arg and deg_mode:
            return "180°"
        return "&pi;"
    if expr == sympy.E or (hasattr(expr, 'name') and expr.name == 'e') or expr.__class__.__name__ == 'Exp1':
        return "e"
    if expr == sympy.I or (hasattr(expr, 'name') and expr.name in ('I', 'i')) or expr.__class__.__name__ in ('ImaginaryUnit', 'imaginaryunit'):
        return "i"
    if expr == sympy.GoldenRatio or (hasattr(expr, 'name') and expr.name == 'phi') or expr.__class__.__name__ == 'GoldenRatio':
        return "&phi;"
    if expr == sympy.EulerGamma or (hasattr(expr, 'name') and expr.name == 'euler') or expr.__class__.__name__ == 'EulerGamma':
        return "&gamma;"
    if expr == sympy.oo or expr.__class__.__name__ == 'Infinity':
        return "&infin;"
    if expr == sympy.nan or expr.__class__.__name__ == 'NaN':
        return "NaN"

    if isinstance(expr, sympy.Integer) or expr.__class__.__name__ == 'Integer':
        val = str(expr)
        if is_trig_arg and deg_mode:
            return f"{val}°"
        return val
        
    if isinstance(expr, sympy.Float) or expr.__class__.__name__ == 'Float':
        val = float(expr)
        if abs(val) < 1e-4 or abs(val) > 1e6:
            s = f"{val:.12e}"
            if 'e' in s:
                base, exp = s.split('e')
                exp = int(exp)
                return f"{base} &times; 10<sup>{exp}</sup>"
        s = f"{expr:.12g}"
        if is_trig_arg and deg_mode:
            return f"{s}°"
        return s
        
    if isinstance(expr, sympy.Symbol) or expr.__class__.__name__ == 'Symbol':
        name = expr.name
        greek_entities = {
            'alpha': '&alpha;', 'beta': '&beta;', 'gamma': '&gamma;', 'delta': '&delta;',
            'epsilon': '&epsilon;', 'zeta': '&zeta;', 'eta': '&eta;', 'theta': '&theta;',
            'iota': '&iota;', 'kappa': '&kappa;', 'lambda': '&lambda;', 'mu': '&mu;',
            'nu': '&nu;', 'xi': '&xi;', 'omicron': '&omicron;', 'pi': '&pi;',
            'rho': '&rho;', 'sigma': '&sigma;', 'tau': '&tau;', 'upsilon': '&upsilon;',
            'phi': '&phi;', 'chi': '&chi;', 'psi': '&psi;', 'omega': '&omega;'
        }
        name_html = greek_entities.get(name.lower(), name)
        if is_trig_arg and deg_mode and name.lower() not in ('pi', 'tau'):
            return f"{name_html}°"
        return name_html

    if isinstance(expr, sympy.Rational) or expr.__class__.__name__ in ('Rational', 'Half'):
        if expr.q == 1:
            return str(expr.p)
        return f"{expr.p}/{expr.q}"
        
    if isinstance(expr, sympy.Add):
        terms = []
        # Group positive and negative terms for better standard mathematical order
        sorted_args = sorted(expr.args, key=lambda x: 1 if x.could_extract_minus_sign() else 0)
        for i, arg in enumerate(sorted_args):
            html = sympy_to_html(arg, deg_mode)
            if html.startswith('-'):
                if i == 0:
                    terms.append(html)
                else:
                    terms.append(f" - {html[1:]}")
            else:
                if i == 0:
                    terms.append(html)
                else:
                    terms.append(f" + {html}")
        return "".join(terms)
        
    if isinstance(expr, sympy.Mul):
        num_terms = []
        den_terms = []
        for arg in expr.args:
            if isinstance(arg, sympy.Pow) and arg.args[1].could_extract_minus_sign():
                inv_pow = sympy.Pow(arg.args[0], -arg.args[1])
                den_terms.append(inv_pow)
            elif isinstance(arg, sympy.Rational) and arg.q > 1:
                if arg.p != 1:
                    num_terms.append(sympy.Integer(abs(arg.p)))
                den_terms.append(sympy.Integer(arg.q))
                if arg.p < 0:
                    num_terms.append(sympy.Integer(-1))
            else:
                num_terms.append(arg)
                
        # Resolve negative signs
        is_negative = False
        final_num_terms = []
        for term in num_terms:
            if term == -1:
                is_negative = not is_negative
            elif isinstance(term, sympy.Integer) and term < 0:
                is_negative = not is_negative
                final_num_terms.append(sympy.Integer(abs(term)))
            elif isinstance(term, sympy.Float) and term < 0:
                is_negative = not is_negative
                final_num_terms.append(sympy.Float(abs(term)))
            else:
                final_num_terms.append(term)
                
        num_htmls = []
        for term in final_num_terms:
            html = sympy_to_html(term, deg_mode)
            if isinstance(term, sympy.Add):
                html = f"({html})"
            num_htmls.append(html)
            
        num_str = ""
        for i, html in enumerate(num_htmls):
            if i > 0:
                prev_term = final_num_terms[i-1]
                curr_term = final_num_terms[i]
                if (isinstance(prev_term, (sympy.Integer, sympy.Float, sympy.Rational)) and 
                    isinstance(curr_term, (sympy.Integer, sympy.Float, sympy.Rational, sympy.Pow))):
                    num_str += " &times; "
                else:
                    num_str += " "
            num_str += html
            
        sign_str = "-" if is_negative else ""
        
        if den_terms:
            den_htmls = []
            for term in den_terms:
                html = sympy_to_html(term, deg_mode)
                if isinstance(term, sympy.Add):
                    html = f"({html})"
                den_htmls.append(html)
            den_str = ""
            for i, html in enumerate(den_htmls):
                if i > 0:
                    prev_term = den_terms[i-1]
                    curr_term = den_terms[i]
                    if (isinstance(prev_term, (sympy.Integer, sympy.Float, sympy.Rational)) and 
                        isinstance(curr_term, (sympy.Integer, sympy.Float, sympy.Rational, sympy.Pow))):
                        den_str += " &times; "
                    else:
                        den_str += " "
                den_str += html
                
            return (
                f"{sign_str}"
                f"<table style='display:inline-table; vertical-align:middle; border-collapse:collapse; border-spacing:0; margin:0 4px;'>"
                f"<tr><td style='border-bottom:1px solid currentColor; text-align:center; padding:0 4px; color:inherit;'>{num_str}</td></tr>"
                f"<tr><td style='text-align:center; padding:0 4px; color:inherit;'>{den_str}</td></tr>"
                f"</table>"
            )
        else:
            return f"{sign_str}{num_str}"
            
    if isinstance(expr, sympy.Pow):
        base, exp = expr.args
        base_html = sympy_to_html(base, deg_mode)
        if isinstance(base, (sympy.Add, sympy.Mul, sympy.Pow)):
            base_html = f"({base_html})"
        exp_html = sympy_to_html(exp, deg_mode)
        return f"{base_html}<sup>{exp_html}</sup>"
        
    if isinstance(expr, sympy.Abs):
        arg_html = sympy_to_html(expr.args[0], deg_mode)
        return f"|{arg_html}|"
        
    if isinstance(expr, sympy.Function) or (hasattr(expr, 'func') and len(expr.args) > 0):
        if hasattr(expr.func, '__name__'):
            func_name = expr.func.__name__.lower()
        else:
            func_name = str(expr.func).lower()
            
        if func_name == 'abs':
            arg_html = sympy_to_html(expr.args[0], deg_mode)
            return f"|{arg_html}|"
        if func_name == 'imaginaryunit':
            return "i"
        if func_name == 'half':
            return "1/2"
        if func_name == 'rational':
            if len(expr.args) == 2:
                return f"{expr.args[0]}/{expr.args[1]}"
                
        is_trig = func_name in ('sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'sinh', 'cosh', 'tanh', 'asinh', 'acosh', 'atanh')
        arg_htmls = [sympy_to_html(arg, deg_mode, is_trig_arg=(is_trig and i==0)) for i, arg in enumerate(expr.args)]
        args_str = ", ".join(arg_htmls)
        return f"{func_name}({args_str})"
        
    return str(expr)


def substitute_unevaluated(expr, target, replacement):
    if expr == target:
        return replacement
    if expr.is_Atom:
        return expr
    if not expr.has(target):
        return expr
        
    new_args = [substitute_unevaluated(arg, target, replacement) for arg in expr.args]
    if all(a is b for a, b in zip(expr.args, new_args)):
        return expr
        
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
            
    if hasattr(expr.func, '__name__'):
        func_name = expr.func.__name__.lower()
    else:
        func_name = str(expr.func).lower()
        
    # Apply trig/func degree scaling only if it contains no free variables/symbols
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
    if hasattr(expr.func, '__name__'):
        func_name = expr.func.__name__.lower()
    else:
        func_name = str(expr.func).lower()
        
    if func_name in eval_dict and not expr.free_symbols:
        func = eval_dict[func_name]
        try:
            val = func(*expr.args)
            if not val.is_Atom and not val.free_symbols:
                return val.evalf()
            return val
        except Exception:
            pass
    return expr.func(*expr.args)


def solve_workspace_expression_steps(expr_str, definitions, deg_mode=True):
    try:
        processed = expr_str.replace('×', '*').replace('÷', '/').replace('−', '-').replace('°', ' deg')
        eval_dict, display_dict = get_sympy_dicts(deg_mode)
        
        # Parse unevaluated
        expr = parse_expr(processed, local_dict=display_dict, transformations=transformations, evaluate=False)
        
        # Substitute definitions
        curr = expr
        for var_name, var_val in definitions.items():
            curr = substitute_unevaluated(curr, sympy.Symbol(var_name), var_val)
            
        steps = [expr]
        if curr != expr:
            steps.append(curr)
            
        # Reduce step by step
        while True:
            target = find_reducible(curr, eval_dict)
            if target is None:
                break
            target_eval = evaluate_node(target, eval_dict)
            curr = substitute_unevaluated(curr, target, target_eval)
            if any(str(step) == str(curr) for step in steps):
                break
            steps.append(curr)
            
        # Convert steps to HTML representation
        html_lines = []
        seen = set()
        for step in steps:
            html = sympy_to_html(step, deg_mode)
            if html not in seen:
                html_lines.append(html)
                seen.add(html)
                
        # Handle symbolic results (e.g. contains variables like x)
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
            
        # Handle numeric results (evaluates to float)
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
    except Exception as e:
        return [f"<span style='color:#f14c4c;'>Parsing Error: {str(e)}</span>"], {}


def solve_equation(expr_str, deg_mode=True):
    """
    Parse the expression, solve it if it contains '=', and return list of HTML display strings.
    """
    res_lines, _ = solve_workspace_equation(expr_str, {}, deg_mode)
    return res_lines


def solve_workspace_equation(expr_str, definitions, deg_mode=True):
    """
    Parse and solve/evaluate an equation string in a workspace,
    using a dict of cumulative variable definitions.
    Returns:
        (list of HTML lines, dict of new definitions discovered)
    """
    eval_dict, display_dict = get_sympy_dicts(deg_mode)
    new_defs = {}
    
    try:
        # Preprocess basic operators
        processed = expr_str.replace('×', '*').replace('÷', '/').replace('−', '-').replace('°', ' deg')
        
        # Check for equation LHS = RHS
        if '=' in processed:
            lhs_str, rhs_str = processed.split('=', 1)
            
            # 1. Parse display expressions (exact symbolic forms for layout)
            lhs_disp = parse_expr(lhs_str, local_dict=display_dict, transformations=transformations)
            rhs_disp = parse_expr(rhs_str, local_dict=display_dict, transformations=transformations)
            
            # 2. Parse evaluation expressions (scaled degrees for actual math execution)
            lhs_eval = parse_expr(lhs_str, local_dict=eval_dict, transformations=transformations)
            rhs_eval = parse_expr(rhs_str, local_dict=eval_dict, transformations=transformations)
            
            # Substitute previous definitions into evaluation expressions
            lhs_eval_subbed = lhs_eval.subs(definitions)
            rhs_eval_subbed = rhs_eval.subs(definitions)
            
            # Generate input equation HTML representation
            eq_html = f"{sympy_to_html(lhs_disp, deg_mode)} = {sympy_to_html(rhs_disp, deg_mode)}"
            
            # Find free variables in the subbed equation
            free_vars = (lhs_eval_subbed - rhs_eval_subbed).free_symbols
            
            if not free_vars:
                # No variables, just evaluate LHS and RHS comparison
                val_lhs = lhs_eval_subbed.evalf()
                val_rhs = rhs_eval_subbed.evalf()
                
                # Check if it represents a simple assignment, e.g. x = 3
                # If LHS is a single symbol and RHS is a number, we can treat it as a definition
                if isinstance(lhs_eval, sympy.Symbol) and val_rhs.is_number:
                    new_defs[lhs_eval.name] = val_rhs
                
                try:
                    lhs_f = float(val_lhs)
                    rhs_f = float(val_rhs)
                    approx_html = f"LHS ≈ {lhs_f:.12g}<br>RHS ≈ {rhs_f:.12g}"
                except Exception:
                    approx_html = f"LHS ≈ {val_lhs}<br>RHS ≈ {val_rhs}"
                    
                return [
                    eq_html,
                    f"&rarr; LHS - RHS = {sympy_to_html(lhs_disp - rhs_disp, deg_mode)}",
                    approx_html
                ], new_defs
            
            # Sort variables and solve for the first one
            var = sorted(list(free_vars), key=lambda x: x.name)[0]
            var_name = var.name
            
            # Rearranged standard form: LHS - RHS = 0 (combined using together)
            std_expr = sympy.together(lhs_disp - rhs_disp)
            std_html = f"&rarr; <div style='display:inline-block; vertical-align:middle;'>{sympy_to_html(std_expr, deg_mode)}</div> = 0"
            
            # Replace custom log10/log2 classes with standard SymPy logs for solving
            lhs_solve = lhs_eval_subbed.replace(log10, lambda x: sympy.log(x, 10)).replace(log2, lambda x: sympy.log(x, 2))
            rhs_solve = rhs_eval_subbed.replace(log10, lambda x: sympy.log(x, 10)).replace(log2, lambda x: sympy.log(x, 2))
            
            # Solve subbed equation symbolically
            try:
                sols = sympy.solve(sympy.Eq(lhs_solve, rhs_solve), var)
            except Exception:
                sols = []
                
            if not sols:
                # Try solver using numerical nsolve fallback with broad initial guesses
                try:
                    eq_to_solve = lhs_solve - rhs_solve
                    guesses = [-100.0, -10.0, -1.0, 0.0, 1.0, 10.0, 100.0]
                    numeric_sols = []
                    for g in guesses:
                        try:
                            nsol = sympy.nsolve(eq_to_solve, var, g)
                            if not any(abs(nsol - s) < 1e-9 for s in numeric_sols):
                                numeric_sols.append(nsol)
                        except Exception:
                            pass
                    if numeric_sols:
                        sols = sorted(numeric_sols)
                except Exception:
                    pass
            
            if not sols:
                return [
                    eq_html,
                    std_html,
                    f"<span style='color:#888888;'>No symbolic solution found for {var_name}.</span>"
                ], new_defs
                
            # Render solutions HTML
            sol_htmls = [sympy_to_html(sol, deg_mode) for sol in sols]
            
            if len(sols) == 1:
                sol_line = f"&rarr; {var_name} = {sol_htmls[0]}"
                # If it's a single constant value, save as definition
                sol_val = sols[0].evalf()
                if sol_val.is_number:
                    new_defs[var_name] = sol_val
            else:
                sol_indices = ",".join(str(i+1) for i in range(len(sols)))
                sol_line = f"&rarr; {var_name}<sub>[{sol_indices}]</sub> = {{ {', '.join(sol_htmls)} }}"
                
            # Compute numerical approximations
            num_vals = []
            for sol in sols:
                try:
                    val = sol.evalf()
                    # Check for complex values
                    if val.is_real:
                        num_vals.append(f"{float(val):.12g}")
                    else:
                        try:
                            num_vals.append(f"{val:.6g}")
                        except TypeError:
                            num_vals.append(sympy_to_html(sol, deg_mode))
                except Exception:
                    num_vals.append(sympy_to_html(sol, deg_mode))
            
            if num_vals:
                approx_line = f"≈ {{ {', '.join(num_vals)} }}"
                return [eq_html, std_html, sol_line, approx_line], new_defs
            else:
                return [eq_html, std_html, sol_line], new_defs
                
        else:
            # Evaluate standard expression step by step
            return solve_workspace_expression_steps(expr_str, definitions, deg_mode)
            
    except Exception as e:
        return [f"<span style='color:#f14c4c;'>Parsing Error: {str(e)}</span>"], new_defs
