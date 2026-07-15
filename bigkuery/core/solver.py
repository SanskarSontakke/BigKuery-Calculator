"""
SymPy Solver - Equation parsing, solving, and rich HTML rendering.
"""

import sympy
import mpmath
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations,
    implicit_multiplication_application, function_exponentiation,
    convert_xor
)

# Enable implicit multiplication (e.g. 2x -> 2*x) and convert XOR (e.g. 10^5 -> 10**5)
transformations = standard_transformations + (implicit_multiplication_application, function_exponentiation, convert_xor)

# Default number of significant digits for numeric results. The GUI overrides this
# from the Settings dialog (1-100), so high-precision answers (e.g. 50-digit sqrt(2))
# are actually delivered rather than truncated to IEEE double.
DEFAULT_PRECISION = 15


def _sci_to_html(s):
    """Convert a scientific string like '1.23e+21' to HTML '1.23 × 10^21'."""
    if 'e' in s or 'E' in s:
        base, _, exp = s.replace('E', 'e').partition('e')
        try:
            exp = int(exp)
        except ValueError:
            return s
        return f"{base} &times; 10<sup>{exp}</sup>"
    return s


def _format_significant(value, precision):
    """Plain string of a real numeric value to `precision` significant digits.

    Avoids Python ``float()`` so precision beyond IEEE double is preserved, and
    uses scientific notation for very large/small magnitudes.
    """
    prec = max(1, int(precision))
    try:
        num = sympy.N(value, prec)
    except Exception:
        return str(value)

    if num == sympy.oo:
        return "∞"
    if num == -sympy.oo:
        return "-∞"
    if num == sympy.zoo or num == sympy.nan:
        return "NaN"

    # Hold enough working digits that nstr can render `prec` significant figures.
    with mpmath.workdps(prec + 10):
        try:
            mpf_val = mpmath.mpf(str(num))
        except Exception:
            return str(num)
        if mpf_val == 0:
            return "0"
        s = mpmath.nstr(mpf_val, prec, strip_zeros=True)
        # mpmath renders whole numbers as 'N.0'; show the clean integer form.
        if s.endswith('.0'):
            s = s[:-2]
        return s


def _eng_parts(value, precision):
    """Return (mantissa_str, eng_exp) for engineering notation.

    eng_exp is a multiple of 3 (mantissa in [1, 1000)), or None when no exponent
    factor is needed / the value is not a finite number.
    """
    prec = max(1, int(precision))
    try:
        num = sympy.N(value, prec)
    except Exception:
        return _format_significant(value, precision), None
    if num in (sympy.oo, -sympy.oo) or num == sympy.zoo or num == sympy.nan:
        return _format_significant(value, precision), None
    with mpmath.workdps(prec + 10):
        try:
            x = mpmath.mpf(str(num))
        except Exception:
            return _format_significant(value, precision), None
        if x == 0:
            return "0", None
        exp = int(mpmath.floor(mpmath.log10(abs(x))))
        eng_exp = (exp // 3) * 3  # floor toward -inf keeps mantissa in [1, 1000)
        mant = x / (mpmath.mpf(10) ** eng_exp)
        mant_s = mpmath.nstr(mant, prec, strip_zeros=True)
        if mant_s.endswith('.0'):
            mant_s = mant_s[:-2]
        return mant_s, (eng_exp if eng_exp != 0 else None)


def _format_eng(value, precision):
    """Engineering notation as HTML: mantissa &times; 10<sup>k</sup>."""
    mant_s, eng_exp = _eng_parts(value, precision)
    if eng_exp is None:
        return mant_s
    return f"{mant_s} &times; 10<sup>{eng_exp}</sup>"


def _eng_to_latex(value, precision):
    """Engineering notation as LaTeX: mantissa \\times 10^{k}."""
    mant_s, eng_exp = _eng_parts(value, precision)
    if eng_exp is None:
        return mant_s
    return f"{mant_s} \\times 10^{{{eng_exp}}}"


def format_approx_html(value, precision=DEFAULT_PRECISION, eng=False):
    """HTML for a numeric result (real or complex) to `precision` significant digits.

    When ``eng`` is True, real results use engineering notation (exponent a
    multiple of 3).
    """
    prec = max(1, int(precision))
    try:
        num = sympy.N(value, prec)
    except Exception:
        return str(value)

    # Complex result: render as a + bi (engineering notation not applied)
    if getattr(num, 'is_real', None) is False:
        re_part = sympy.re(num)
        im_part = sympy.im(num)
        im_abs_html = _sci_to_html(_format_significant(abs(im_part), prec))
        im_coeff = "" if im_abs_html == "1" else im_abs_html  # render 1i as i
        if re_part == 0:
            lead = "-" if im_part < 0 else ""
            return f"{lead}{im_coeff}i"
        re_html = _sci_to_html(_format_significant(re_part, prec))
        sign = "-" if im_part < 0 else "+"
        return f"{re_html} {sign} {im_coeff}i"

    if eng:
        return _format_eng(num, prec)
    return _sci_to_html(_format_significant(num, prec))


def _sci_to_latex(s):
    """Convert a scientific string like '1.23e+21' to LaTeX '1.23 \\times 10^{21}'."""
    if 'e' in s or 'E' in s:
        base, _, exp = s.replace('E', 'e').partition('e')
        try:
            exp = int(exp)
        except ValueError:
            return s
        return f"{base} \\times 10^{{{exp}}}"
    return s


def sympy_to_latex(expr, deg_mode=True):
    """Render a SymPy expression to LaTeX for KaTeX display.

    Delegates to ``sympy.latex`` (proper radicals, fractions, integrals,
    derivatives, Greek letters), which is far more robust than the hand-rolled
    HTML renderer.
    """
    if expr is None:
        return ""
    if isinstance(expr, str):
        return expr
    try:
        return sympy.latex(expr, mul_symbol='times')
    except Exception:
        try:
            return sympy.latex(expr)
        except Exception:
            return str(expr)


def format_approx_latex(value, precision=DEFAULT_PRECISION, eng=False):
    """LaTeX for a numeric result (real or complex) to `precision` significant digits."""
    prec = max(1, int(precision))
    try:
        num = sympy.N(value, prec)
    except Exception:
        return str(value)

    if getattr(num, 'is_real', None) is False:
        re_part = sympy.re(num)
        im_part = sympy.im(num)
        im_abs = _format_significant(abs(im_part), prec)
        im_coeff = "" if im_abs == "1" else _sci_to_latex(im_abs)
        if re_part == 0:
            lead = "-" if im_part < 0 else ""
            return f"{lead}{im_coeff}i"
        re_l = _sci_to_latex(_format_significant(re_part, prec))
        sign = "-" if im_part < 0 else "+"
        return f"{re_l} {sign} {im_coeff}i"

    if eng:
        return _eng_to_latex(num, prec)
    return _sci_to_latex(_format_significant(num, prec))


class _Renderer:
    """Builds display lines in either HTML or LaTeX from the same solver logic.

    Keeping a single rendering abstraction lets the HTML path stay byte-identical
    (so existing tests are unaffected) while a LaTeX path is produced for KaTeX.
    """

    def __init__(self, latex: bool):
        self.latex = latex
        self.arrow = "\\to " if latex else "&rarr; "
        self.approx = "\\approx " if latex else "≈ "

    def expr(self, e, deg_mode):
        return sympy_to_latex(e, deg_mode) if self.latex else sympy_to_html(e, deg_mode)

    def num(self, v, precision, eng):
        if self.latex:
            return format_approx_latex(v, precision, eng)
        return format_approx_html(v, precision, eng)

    def text(self, s):
        return f"\\text{{{s}}}" if self.latex else s

    def subscript(self, base, sub):
        return f"{base}_{{{sub}}}" if self.latex else f"{base}<sub>{sub}</sub>"

    def set_braces(self, items):
        inner = ", ".join(items)
        return f"\\{{ {inner} \\}}" if self.latex else f"{{ {inner} }}"

    def std_form(self, inner_html):
        # "<expr> = 0", with an alignment wrapper only needed for the HTML table.
        if self.latex:
            return f"{inner_html} = 0"
        return (
            f"<div style='display:inline-block; vertical-align:middle;'>"
            f"{inner_html}</div> = 0"
        )

    def lhs_rhs(self, n1, n2):
        if self.latex:
            return f"\\text{{LHS}} \\approx {n1},\\ \\text{{RHS}} \\approx {n2}"
        return f"LHS ≈ {n1}<br>RHS ≈ {n2}"

    def muted(self, msg):
        return f"\\text{{{msg}}}" if self.latex else f"<span style='color:#888888;'>{msg}</span>"

    def error(self, msg):
        if self.latex:
            return f"\\text{{{msg}}}"
        return f"<span style='color:#f14c4c;'>{msg}</span>"


_HTML_RENDERER = _Renderer(latex=False)
_LATEX_RENDERER = _Renderer(latex=True)


def _renderer_for(fmt):
    return _LATEX_RENDERER if fmt == 'latex' else _HTML_RENDERER


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


# Cache of built dict templates, keyed by deg_mode. Building these dicts creates
# ~40 lambda closures + SymPy objects; doing it on every keystroke (the GUI calls
# this twice per equation per evaluate) is wasteful. We build once and hand out
# cheap shallow copies, since parse_expr augments the local_dict it is given with
# auto-created Symbols (which would otherwise pollute a shared cached dict).
_dict_templates: dict = {}


def get_sympy_dicts(deg_mode=True):
    """Get dictionaries for parsing (eval vs display), cached per angle mode."""
    key = bool(deg_mode)
    if key not in _dict_templates:
        _dict_templates[key] = _build_sympy_dicts(key)
    eval_template, display_template = _dict_templates[key]
    return dict(eval_template), dict(display_template)


def _build_sympy_dicts(deg_mode=True):
    """Construct the parsing dictionaries (eval vs display) from scratch."""
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
        'sign': sympy.sign, 'binomial': sympy.binomial,
        'gcd': sympy.gcd, 'lcm': sympy.lcm,
        # Calculus (computed with radian / standard semantics)
        'diff': sympy.diff, 'integrate': sympy.integrate, 'limit': sympy.limit,
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
        'sign': sympy.sign, 'binomial': sympy.binomial,
        'gcd': sympy.gcd, 'lcm': sympy.lcm,
        # Calculus (computed with radian / standard semantics)
        'diff': sympy.diff, 'integrate': sympy.integrate, 'limit': sympy.limit,
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


def evaluate_node(expr, eval_dict, precision=DEFAULT_PRECISION):
    if hasattr(expr.func, '__name__'):
        func_name = expr.func.__name__.lower()
    else:
        func_name = str(expr.func).lower()

    if func_name in eval_dict and not expr.free_symbols:
        func = eval_dict[func_name]
        try:
            val = func(*expr.args)
            if not val.is_Atom and not val.free_symbols:
                # Evaluate to the requested precision, not the default ~15 digits,
                # so intermediate reductions don't cap the final result's accuracy.
                return val.evalf(precision)
            return val
        except Exception:
            pass
    return expr.func(*expr.args)


# --- Result memoization -------------------------------------------------------
# Solving/reducing an expression with SymPy is expensive (parse + solve + render).
# The GUI re-solves every card on every evaluate (and several times per multi-pass
# propagation). Identical (expression, definitions, angle-mode) inputs always yield
# identical output, so we memoize. Caches are bounded and cleared wholesale when full.
_MEMO_MAX = 512
_expr_steps_memo: dict = {}
_equation_memo: dict = {}


def _defs_signature(definitions):
    """A stable, hashable signature for a variable-definitions dict."""
    if not definitions:
        return ()
    return tuple(sorted((str(k), str(v)) for k, v in definitions.items()))


def _memo_get(memo, key):
    return memo.get(key)


def _memo_put(memo, key, value):
    if len(memo) >= _MEMO_MAX:
        memo.clear()
    memo[key] = value
    return value


def clear_solver_caches():
    """Clear all memoized solver results (call when precision/settings change)."""
    _expr_steps_memo.clear()
    _equation_memo.clear()


def solve_workspace_expression_steps(expr_str, definitions, deg_mode=True, precision=DEFAULT_PRECISION, eng=False, fmt='html'):
    key = (expr_str, _defs_signature(definitions), bool(deg_mode), int(precision), bool(eng), fmt)
    cached = _memo_get(_expr_steps_memo, key)
    if cached is not None:
        return cached
    result = _solve_workspace_expression_steps_impl(expr_str, definitions, deg_mode, precision, eng, fmt)
    return _memo_put(_expr_steps_memo, key, result)


def _solve_workspace_expression_steps_impl(expr_str, definitions, deg_mode=True, precision=DEFAULT_PRECISION, eng=False, fmt='html'):
    r = _renderer_for(fmt)
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

        # Reduce step by step. Track seen string-forms in a set for O(1) dedup and
        # cap iterations so a non-converging reduction can never hang the UI.
        seen_forms = {str(s) for s in steps}
        for _ in range(200):
            target = find_reducible(curr, eval_dict)
            if target is None:
                break
            target_eval = evaluate_node(target, eval_dict, precision)
            curr = substitute_unevaluated(curr, target, target_eval)
            curr_form = str(curr)
            if curr_form in seen_forms:
                break
            seen_forms.add(curr_form)
            steps.append(curr)
            
        # Convert steps to display representation (HTML or LaTeX)
        html_lines = []
        seen = set()
        for step in steps:
            html = r.expr(step, deg_mode)
            if html not in seen:
                html_lines.append(html)
                seen.add(html)

        # Handle symbolic results (e.g. contains variables like x)
        if not curr.is_number:
            simplified = sympy.simplify(curr)
            if simplified != curr:
                html = r.expr(simplified, deg_mode)
                if html not in seen:
                    html_lines.append(f"= {html}")
            elif len(html_lines) == 1:
                html_lines.append(f"= {html_lines[0]}")
            else:
                html_lines[-1] = f"= {html_lines[-1]}"
            return html_lines, {}

        # Handle numeric results to the requested precision (no float() truncation).
        approx_line = f"{r.approx}{r.num(curr, precision, eng)}"
        if approx_line not in seen:
            html_lines.append(approx_line)

        return html_lines, {}
    except Exception as e:
        return [r.error(f"Parsing Error: {str(e)}")], {}


def solve_equation(expr_str, deg_mode=True, precision=DEFAULT_PRECISION, eng=False, fmt='html'):
    """
    Parse the expression, solve it if it contains '=', and return list of display strings.
    """
    res_lines, _ = solve_workspace_equation(expr_str, {}, deg_mode, precision, eng, fmt)
    return res_lines


def solve_workspace_equation(expr_str, definitions, deg_mode=True, precision=DEFAULT_PRECISION, eng=False, fmt='html'):
    """
    Parse and solve/evaluate an equation string in a workspace, using a dict of
    cumulative variable definitions. Memoized on (expr, definitions, angle mode,
    precision, eng, fmt).
    Returns:
        (list of display lines, dict of new definitions discovered)
    """
    key = (expr_str, _defs_signature(definitions), bool(deg_mode), int(precision), bool(eng), fmt)
    cached = _memo_get(_equation_memo, key)
    if cached is not None:
        return cached
    result = _solve_workspace_equation_impl(expr_str, definitions, deg_mode, precision, eng, fmt)
    return _memo_put(_equation_memo, key, result)


def _split_equation_system(processed):
    """Detect a semicolon-separated system of equations, e.g. 'x+y=5; x-y=1'.

    Returns the list of equation strings, or None if this isn't a system
    (fewer than 2 parts, or some part lacks an '=').
    """
    if ';' not in processed:
        return None
    parts = [p.strip() for p in processed.split(';') if p.strip()]
    if len(parts) < 2:
        return None
    if not all('=' in p for p in parts):
        return None
    return parts


def _solve_system_impl(parts, definitions, deg_mode, precision, eng, fmt, r, eval_dict, display_dict):
    """Solve a system of equations simultaneously via sympy.solve([...], [vars])."""
    new_defs = {}
    try:
        lhs_disp_list, rhs_disp_list = [], []
        eqs_solve = []
        all_free = set()

        for part in parts:
            lhs_str, rhs_str = part.split('=', 1)

            lhs_disp = parse_expr(lhs_str, local_dict=display_dict, transformations=transformations)
            rhs_disp = parse_expr(rhs_str, local_dict=display_dict, transformations=transformations)
            lhs_eval = parse_expr(lhs_str, local_dict=eval_dict, transformations=transformations)
            rhs_eval = parse_expr(rhs_str, local_dict=eval_dict, transformations=transformations)

            lhs_sub = lhs_eval.subs(definitions)
            rhs_sub = rhs_eval.subs(definitions)

            # Replace custom log10/log2 classes with standard SymPy logs for solving
            lhs_solve = lhs_sub.replace(log10, lambda x: sympy.log(x, 10)).replace(log2, lambda x: sympy.log(x, 2))
            rhs_solve = rhs_sub.replace(log10, lambda x: sympy.log(x, 10)).replace(log2, lambda x: sympy.log(x, 2))

            eqs_solve.append(sympy.Eq(lhs_solve, rhs_solve))
            all_free |= (lhs_sub - rhs_sub).free_symbols
            lhs_disp_list.append(lhs_disp)
            rhs_disp_list.append(rhs_disp)

        eq_lines = [f"{r.expr(l, deg_mode)} = {r.expr(rr, deg_mode)}" for l, rr in zip(lhs_disp_list, rhs_disp_list)]
        joiner = " ;\\ " if r.latex else " ; "
        eq_block = joiner.join(eq_lines)

        if not all_free:
            return [eq_block, r.muted("No unknowns to solve for.")], new_defs

        vars_sorted = sorted(all_free, key=lambda v: v.name)

        try:
            sols = sympy.solve(eqs_solve, vars_sorted, dict=True)
        except Exception:
            sols = []

        if not sols:
            return [eq_block, r.muted("No solution found for the system.")], new_defs

        if len(sols) == 1:
            sol = sols[0]
            lines = [eq_block]
            for v in vars_sorted:
                if v not in sol:
                    continue
                val = sol[v]
                if getattr(val, 'free_symbols', None):
                    val_str = r.expr(val, deg_mode)
                else:
                    val_str = r.num(val, precision, eng)
                    try:
                        new_defs[v.name] = val.evalf(precision)
                    except Exception:
                        pass
                lines.append(f"{r.arrow}{v.name} = {val_str}")
            return lines, new_defs

        # Multiple solution sets (e.g. a nonlinear system)
        lines = [eq_block]
        for i, sol in enumerate(sols):
            piece = ", ".join(
                f"{v.name} = {r.expr(sol[v], deg_mode)}" for v in vars_sorted if v in sol
            )
            lines.append(f"{r.subscript('Solution', str(i + 1))}: {piece}")
        return lines, new_defs

    except Exception as e:
        return [r.error(f"Parsing Error: {str(e)}")], new_defs


def _solve_workspace_equation_impl(expr_str, definitions, deg_mode=True, precision=DEFAULT_PRECISION, eng=False, fmt='html'):
    r = _renderer_for(fmt)
    eval_dict, display_dict = get_sympy_dicts(deg_mode)
    new_defs = {}
    
    try:
        # Preprocess basic operators. Normalize '==' to '=' so an equality typed as
        # 'x == 5' is treated as the equation 'x = 5' rather than split mid-operator.
        processed = expr_str.replace('×', '*').replace('÷', '/').replace('−', '-').replace('°', ' deg')
        processed = processed.replace('==', '=')

        # Systems of equations: "x + y = 5; x - y = 1" solves both simultaneously
        # rather than the single-= path mis-splitting at the first '='.
        system_parts = _split_equation_system(processed)
        if system_parts is not None:
            return _solve_system_impl(system_parts, definitions, deg_mode, precision, eng, fmt, r, eval_dict, display_dict)

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
            
            # Generate input equation representation
            eq_html = f"{r.expr(lhs_disp, deg_mode)} = {r.expr(rhs_disp, deg_mode)}"
            
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
                
                approx_html = r.lhs_rhs(
                    r.num(val_lhs, precision, eng),
                    r.num(val_rhs, precision, eng),
                )

                return [
                    eq_html,
                    f"{r.arrow}{r.text('LHS - RHS')} = {r.expr(lhs_disp - rhs_disp, deg_mode)}",
                    approx_html
                ], new_defs
            
            # Choose which variable to solve for. If the left-hand side is a single
            # symbol (an assignment-like form, e.g. "y = m*x + b"), solve for that
            # symbol; otherwise fall back to the alphabetically-first free variable.
            if isinstance(lhs_eval, sympy.Symbol) and lhs_eval in free_vars:
                var = lhs_eval
            else:
                var = sorted(list(free_vars), key=lambda x: x.name)[0]
            var_name = var.name
            
            # Rearranged standard form: LHS - RHS = 0 (combined using together)
            std_expr = sympy.together(lhs_disp - rhs_disp)
            std_html = f"{r.arrow}{r.std_form(r.expr(std_expr, deg_mode))}"
            
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
                    r.muted(f"No symbolic solution found for {var_name}.")
                ], new_defs

            # Render solutions
            sol_htmls = [r.expr(sol, deg_mode) for sol in sols]

            if len(sols) == 1:
                sol_line = f"{r.arrow}{var_name} = {sol_htmls[0]}"
                # If it's a single constant value, save as definition
                sol_val = sols[0].evalf()
                if sol_val.is_number:
                    new_defs[var_name] = sol_val
            else:
                sol_indices = ",".join(str(i+1) for i in range(len(sols)))
                sol_line = f"{r.arrow}{r.subscript(var_name, f'[{sol_indices}]')} = {r.set_braces(sol_htmls)}"

            # Compute numerical approximations to the requested precision. Symbolic
            # solutions (still containing free variables) are rendered as expressions
            # rather than forced through the numeric formatter.
            num_vals = []
            for sol in sols:
                try:
                    if getattr(sol, 'free_symbols', None):
                        num_vals.append(r.expr(sol, deg_mode))
                    else:
                        num_vals.append(r.num(sol, precision, eng))
                except Exception:
                    num_vals.append(r.expr(sol, deg_mode))

            if num_vals:
                approx_line = f"{r.approx}{r.set_braces(num_vals)}"
                return [eq_html, std_html, sol_line, approx_line], new_defs
            else:
                return [eq_html, std_html, sol_line], new_defs

        else:
            # Evaluate standard expression step by step
            return solve_workspace_expression_steps(expr_str, definitions, deg_mode, precision, eng, fmt)

    except Exception as e:
        return [r.error(f"Parsing Error: {str(e)}")], new_defs
