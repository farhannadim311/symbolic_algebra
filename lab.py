"""
6.101 Lab:
Symbolic Algebra
"""

# NO ADDITIONAL IMPORTS ALLOWED!

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def tokenizing(expr):
    tokenize = []
    num = ""
    for idx, val in enumerate(expr):
        if val == "-":
            if idx + 1 < len(expr) and (expr[idx + 1].isdigit() or expr[idx + 1] == "."):
                num += val
            else:
                tokenize.append(val)
        elif val.isdigit() or val == ".":
            num += val
        elif val == " ":
            if num:
                tokenize.append(num)
                num = ""
        else:
            if num:
                tokenize.append(num)
                num = ""
            tokenize.append(val)

    if num:
        tokenize.append(num)

    return tokenize
    
def parse(tokens):
    def parse_expression(index):
        token = tokens[index]

        # Case 1: Number
        try:
            value = float(token)
            return Num(value), index + 1
        except ValueError:
            pass

        # Case 2: Variable
        if token.isalpha():
            return Var(token), index + 1

        # Case 3: Compound expression ( ( E1 op E2 ) )
        if token == "(":
            left_expr, next_index = parse_expression(index + 1)
            op = tokens[next_index]
            right_expr, next_index = parse_expression(next_index + 1)
            if tokens[next_index] != ")":
                raise ValueError("Expected closing parenthesis")
            if op == "+":
                return Add(left_expr, right_expr), next_index + 1
            elif op == "-":
                return Sub(left_expr, right_expr), next_index + 1
            elif op == "*":
                return Mul(left_expr, right_expr), next_index + 1
            elif op == "/":
                return Div(left_expr, right_expr), next_index + 1
            else:
                raise ValueError(f"Unknown operator: {op}")

        raise ValueError(f"Unexpected token: {token}")

    parsed_expr, next_index = parse_expression(0)
    return parsed_expr
       
def make_expression(s):
    lst = tokenizing(s)
    return (parse(lst))
            



class Expr:
    def precedence(self):
        return float("inf")

    def __add__(self, other):
        return Add(self, other)

    def __radd__(self, other):
        return Add(other, self)

    def __sub__(self, other):
        return Sub(self, other)

    def __rsub__(self, other):
        return Sub(other, self)

    def __mul__(self, other):
        return Mul(self, other)

    def __rmul__(self, other):
        return Mul(other, self)

    def __truediv__(self, other):
        return Div(self, other)

    def __rtruediv__(self, other):
        return Div(other, self)
    



class Var(Expr):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Var('{self.name}')"

    def evaluate(self, mapping):
        if self.name not in mapping:
            raise SymbolicEvaluationError(f"Variable '{self.name}' not found")
        return mapping[self.name]

    def deriv(self, var):
        return Num(1) if var == self.name else Num(0)

    def simplify(self):
        return self


class Num(Expr):
    def __init__(self, n):
        self.n = n

    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return f"Num({self.n})"

    def evaluate(self, mapping):
        return self.n

    def deriv(self, var):
        return Num(0)

    def __eq__(self, other):
        return isinstance(other, Num) and self.n == other.n

    def simplify(self):
        return self


class BinOp(Expr):
    def __init__(self, left, right):
        if isinstance(left, (int, float)):
            left = Num(left)
        elif isinstance(left, str):
            left = Var(left)
        if isinstance(right, (int, float)):
            right = Num(right)
        elif isinstance(right, str):
            right = Var(right)
        self.left = left
        self.right = right

    def __str__(self):
        left_str = str(self.left)
        right_str = str(self.right)
        if self.left.precedence() < self.precedence():
            left_str = f"({left_str})"
        right_prec = self.right.precedence()
        if right_prec < self.precedence() or (
            right_prec == self.precedence() and self.op_symbol in "-/"
        ):
            right_str = f"({right_str})"
        return f"{left_str} {self.op_symbol} {right_str}"

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.left)}, {repr(self.right)})"

    def evaluate(self, mapping):
        return self.operator(self.left.evaluate(mapping), self.right.evaluate(mapping))

    def simplify(self):
        left  = self.left.simplify()
        right = self.right.simplify()
        if isinstance(left, Num) and isinstance(right, Num):
            return Num(self.operator(left.n, right.n))

        kind = type(self).__name__

        if kind == "Add":
            if isinstance(left,  Num) and left.n  == 0: return right
            if isinstance(right, Num) and right.n == 0: return left

        elif kind == "Sub":
            if isinstance(right, Num) and right.n == 0: return left          # E – 0 → E

        elif kind == "Mul":
            if (isinstance(left,  Num) and left.n  == 0) or \
               (isinstance(right, Num) and right.n == 0):
                return Num(0)                                               # 0 · E → 0
            if isinstance(left,  Num) and left.n  == 1: return right        # 1 · E → E
            if isinstance(right, Num) and right.n == 1: return left

        elif kind == "Div":
            if isinstance(left,  Num) and left.n  == 0: return Num(0)       # 0 / E → 0
            if isinstance(right, Num) and right.n == 1: return left         # E / 1 → E

        return self.__class__(left, right)
    
 
        



    

class Add(BinOp):
    op_symbol = "+"

    def precedence(self):
        return 1

    @staticmethod
    def operator(a, b):
        return a + b

    def deriv(self, var):
        return Add(self.left.deriv(var), self.right.deriv(var))


class Sub(BinOp):
    op_symbol = "-"

    def precedence(self):
        return 1

    @staticmethod
    def operator(a, b):
        return a - b

    def deriv(self, var):
        return Sub(self.left.deriv(var), self.right.deriv(var))


class Mul(BinOp):
    op_symbol = "*"

    def precedence(self):
        return 2

    @staticmethod
    def operator(a, b):
        return a * b

    def deriv(self, var):
        return Add(
            Mul(self.left, self.right.deriv(var)),
            Mul(self.right, self.left.deriv(var))
        )


class Div(BinOp):
    op_symbol = "/"

    def precedence(self):
        return 2

    @staticmethod
    def operator(a, b):
        return a / b

    def deriv(self, var):
        return Div(
            Sub(
                Mul(self.right, self.left.deriv(var)),
                Mul(self.left, self.right.deriv(var))
            ),
            Mul(self.right, self.right)
        )


class SymbolicEvaluationError(Exception):
    pass


if __name__ == "__main__":
    pass
