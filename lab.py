"""
6.101 Lab:
Symbolic Algebra
"""

# import doctest # optional import
# import typing # optional import
# import pprint # optional import
# import string # optional import
# import abc # optional import

# NO ADDITIONAL IMPORTS ALLOWED!
# You are welcome to modify the classes below, as well as to implement new
# classes and helper functions as necessary.


class SymbolicEvaluationError(Exception):
    """
    An expression indicating that something has gone wrong when evaluating a symbolic algebra expression
    """
    pass

class Expr:
    """
    Represents an Expression in a symbolic algebra system
    """
    precedence = 10

 

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
    """
    Represents a string as a variable in a symbolic algebra system
    """
    def __init__(self, name):
        """
        Initializer.  Store an instance variable called `name`, containing the
        value passed in to the initializer.
        """
        self.name = name

    def __str__(self):
        return self.name
    
    def evaluate(self, mapping):
        if(self.name not in mapping):
            raise SymbolicEvaluationError
        else:
            return mapping[self.name]

    def __repr__(self):
        return f"Var('{self.name}')"
    
    def deriv(self, v):
        if(v == self.name):
            return Num(1)
        else:
            return Num(0)

    def simplify(self):
        return self

class Num(Expr):
    """
    Represents integers and floats as Num in symbolic algebra system
    """
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `n`, containing the
        value passed in to the initializer.
        """
        self.n = n

    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return f"Num({self.n})"
    
    def evaluate(self, mapping):
        return self.n
    
    def deriv(self, v):
        return Num(0)
    
    def simplify(self):
        return self

#My goal is to do Add(2, 'x) and it will create an instance of Add(Num(2) , Var('x'))   
class BinOp(Expr):
    """
    Represents a binary operation ie a left expression and a right expression with some operations such as add, mul, sub, div
    """
    def __init__(self, left, right):
        """
        Initializer, stores left and right as either EXPR or NUM or VAR
        """
        if(isinstance(left, int) or isinstance(left, float)):
            self.left = Num(left) #example of left is 2 or some variable ('x')
        elif(isinstance(left, str)):
            self.left = Var(left)
        else:
            self.left = left
        if(isinstance(right, int) or isinstance(right, float)):
            self.right = Num(right) # example of right is 4 or some variable 'x'
        elif(isinstance(right, str)):
            self.right = Var(right)
        else:
            self.right = right
    
    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.left)}, {repr(self.right)})"
    
    
    
    def __str__(self):
        left = str(self.left)
        right = str(self.right)

        if((self.precedence % 2 == 1 and self.operator == '/' or self.operator == '-') and self.precedence == self.right.precedence):
            right = f"({right})"
        if(self.left.precedence < self.precedence):
            left = f"({left})"
        if(self.right.precedence < self.precedence):
            right = f"({right})"
        return f"{left} {self.operator} {right}"
        
    
        

class Add(BinOp):
    """
    Represents Addition
    """
    operator = '+'
    precedence = 1
    
    def evaluate(self, mapping):
        return self.left.evaluate(mapping) + self.right.evaluate(mapping)
    
    def deriv(self, v):
        return self.left.deriv(v) + self.right.deriv(v)
    
    def simplify(self):
        left = self.left.simplify()
        right = self.right.simplify()
        if(isinstance(left, Num) and isinstance(right, Num)):
            return Num(left.n + right.n)
        if(isinstance(left, Num) and not(isinstance(right, Num))):
            if(left.n == 0):
                res = right
                return res
        if(isinstance(right, Num) and not(isinstance(left, Num))):
            if(right.n == 0):
                res = left
                return res
        return left + right


class Sub(BinOp):
    """
    Represents Subtraction
    """
    operator = "-"
    precedence = 1

    def evaluate(self, mapping):
        return self.left.evaluate(mapping) - self.right.evaluate(mapping)
    
    def deriv(self, v):
        return self.left.deriv(v) - self.right.deriv(v)
    
    def simplify(self):
        left = self.left.simplify()
        right = self.right.simplify()
        if(isinstance(left, Num) and isinstance(right, Num)):
            return Num(left.n - right.n)
        if(isinstance(right, Num) and not isinstance(left, Num)):
            if(right.n == 0):
                res = left
                return res
        return left - right

class Mul(BinOp):
    """
    Represents Multiplication
    """
    operator = '*'
    precedence = 3
    def evaluate(self, mapping):
        return self.left.evaluate(mapping) * self.right.evaluate(mapping)
    
    def deriv(self, v):
        return self.left * self.right.deriv(v) + self.right * self.left.deriv(v)
    
    def simplify(self):
        left = self.left.simplify()
        right = self.right.simplify()
        if(isinstance(left, Num) and isinstance(right, Num)):
            return Num(left.n * right.n)
        if(isinstance(left, Num) and not isinstance(right, Num)):
            if(left.n == 1):
                res = right
                return res
            if(left.n == 0):
                res = Num(0)
                return res
        
        if(isinstance(right, Num) and not isinstance(left, Num)):
            if(right.n == 1):
                res = left
                return res
            if(right.n == 0):
                res = Num(0)
                return res
        
        return left * right


class Div(BinOp):
    """
    Represents Division
    """
    operator = '/'
    precedence = 3

    def evaluate(self, mapping):
        return self.left.evaluate(mapping) / self.right.evaluate(mapping)
    
    def deriv(self, v):
        return (self.right * self.left.deriv(v) - self.left * self.right.deriv(v)) / (self.right * self.right)

    def simplify(self):
        left = self.left.simplify()
        right = self.right.simplify()
        if(isinstance(left, Num) and isinstance(right, Num)):
            return Num(left.n / right.n)
        if(isinstance(left, Num) and not isinstance(right, Num)):
            if(left.n == 0):
                res = Num(0)
                return res
        
        if(isinstance(right, Num) and not isinstance(left, Num)):
            if(right.n == 1):
                res = left
                return res
        return left / right


def tokenize(exp):
    res = []
    build = ""
    for idx, char in enumerate(exp):
        if(char == ' '):
            continue
        if((char == '-' and exp[idx + 1].isdigit()) or (char == '-' and exp[idx + 1] == '.')):
            build = build + char
            continue
        
        if(char.isdigit() or char == '.'):
            build = build + char
            continue
        
        if(build):
            res.append(build)
            build = ""
        res.append(char)
    if(build):
        res.append(build)
    
    return res


def parse(tokens):
    operations = {'*': lambda a, b : a * b,
                  "/" : lambda a, b : a / b,
                  "-": lambda a, b : a - b,
                  "+": lambda a, b : a + b
    }
    def parse_expression(index): #example (x * (-20.2 * y))
        if(tokens[index].isalpha()):
            return Var(tokens[index]), index + 1
        
        else:
            try:
                f = float(tokens[index])
                if(f.is_integer()):
                    f = int(f)
                return Num(f), index + 1
            except ValueError:
                pass

        if(tokens[index] == '('):
            left,lidx = parse_expression(index + 1)
            op = tokens[lidx]
            right,ridx = parse_expression(lidx + 1)
            return operations[op](left, right),ridx + 1





      


    parsed_expression, next_index = parse_expression(0)
    return parsed_expression

def make_expression(exp):
    tokens = tokenize(exp)
    return parse(tokens)


if __name__ == "__main__":
    token2 = tokenize("((x + A) * (y + z))")
    print(parse(token2))
