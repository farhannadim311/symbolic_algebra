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



if __name__ == "__main__":
    z = Add(Add(Num(2), Num(-2)), Add(Var('x'), Num(0))).simplify()
    print(z)


















































    #expected = Sub(Num(1), Mul(Mul(Num(-1), Div(Div(Sub(Sub(Sub(Sub(Sub(Mul(Div(Add(Add(Sub(Num(1), Var('j')), Var('o')), Var('c')), Add(Add(Div(Var('l'), Var('u')), Var('X')), Div(Sub(Var('g'), Num(1)), Sub(Var('B'), Var('T'))))), Add(Var('b'), Var('a'))), Add(Mul(Num(-1), Sub(Mul(Num(-1), Div(Var('s'), Var('L'))), Sub(Sub(Var('b'), Num(-1)), Div(Var('P'), Var('X'))))), Mul(Add(Var('I'), Var('N')), Var('G')))), Add(Sub(Var('s'), Mul(Add(Add(Var('u'), Var('H')), Mul(Sub(Num(1), Var('l')), Div(Num(-1), Var('B')))), Var('A'))), Mul(Div(Add(Sub(Var('T'), Num(1)), Num(-1)), Num(-1)), Mul(Div(Var('O'), Add(Add(Var('b'), Var('Q')), Var('j'))), Var('L'))))), Var('q')), Sub(Div(Num(1), Add(Var('e'), Sub(Add(Var('Y'), Sub(Var('e'), Sub(Sub(Var('Z'), Var('v')), Add(Var('P'), Var('M'))))), Add(Add(Num(1), Sub(Var('U'), Num(-1))), Mul(Add(Div(Num(1), Var('m')), Mul(Var('e'), Var('M'))), Var('U')))))), Var('c'))), Num(-1)), Add(Div(Var('v'), Div(Var('D'), Num(-1))), Mul(Sub(Add(Sub(Var('M'), Sub(Div(Var('f'), Mul(Var('w'), Var('P'))), Div(Div(Var('p'), Var('T')), Add(Add(Sub(Num(-1), Var('B')), Var('u')), Div(Sub(Var('i'), Var('r')), Sub(Var('e'), Num(-1))))))), Sub(Sub(Num(2), Var('G')), Mul(Var('Z'), Sub(Mul(Mul(Var('u'), Num(-1)), Num(2)), Mul(Var('z'), Var('N')))))), Div(Mul(Add(Mul(Num(-1), Sub(Var('q'), Var('I'))), Add(Sub(Sub(Var('l'), Var('V')), Sub(Var('F'), Var('g'))), Add(Num(1), Var('k')))), Var('e')), Div(Mul(Mul(Div(Var('w'), Var('V')), Sub(Num(0), Var('s'))), Add(Var('Y'), Sub(Num(-1), Add(Var('G'), Var('R'))))), Sub(Var('t'), Add(Add(Num(-1), Add(Num(1), Var('c'))), Mul(Div(Var('E'), Var('i')), Num(-1))))))), Var('L')))), Num(-1))), Sub(Div(Mul(Add(Mul(Mul(Div(Div(Sub(Add(Add(Sub(Var('I'), Num(1)), Div(Num(1), Var('Q'))), Sub(Var('G'), Num(-1))), Var('J')), Var('c')), Mul(Num(-1), Div(Num(-1), Div(Sub(Var('E'), Div(Var('E'), Var('l'))), Add(Div(Var('h'), Num(-1)), Add(Var('V'), Num(-1))))))), Var('E')), Mul(Div(Var('k'), Mul(Div(Add(Var('d'), Var('A')), Add(Mul(Mul(Num(-1), Var('r')), Div(Num(1), Var('D'))), Num(-1))), Sub(Add(Div(Var('A'), Var('Z')), Add(Var('L'), Var('T'))), Div(Div(Add(Num(1), Var('b')), Num(-1)), Div(Mul(Var('I'), Var('n')), Add(Var('B'), Var('E'))))))), Div(Add(Mul(Add(Num(2), Mul(Div(Num(-1), Var('S')), Sub(Var('E'), Var('d')))), Add(Mul(Var('F'), Add(Var('n'), Var('n'))), Sub(Num(-1), Var('I')))), Add(Num(1), Var('e'))), Var('Y')))), Var('x')), Sub(Sub(Mul(Sub(Sub(Num(0), Mul(Sub(Num(0), Var('E')), Add(Var('J'), Num(1)))), Var('P')), Sub(Sub(Div(Sub(Mul(Sub(Sub(Var('P'), Var('t')), Var('V')), Num(-1)), Sub(Var('o'), Div(Num(1), Var('m')))), Sub(Sub(Mul(Num(-1), Div(Var('f'), Var('e'))), Div(Mul(Var('f'), Num(-1)), Div(Var('X'), Var('J')))), Mul(Mul(Var('G'), Var('n')), Sub(Var('O'), Var('y'))))), Num(-1)), Var('Z'))), Sub(Num(1), Div(Add(Num(-1), Var('F')), Sub(Num(1), Sub(Mul(Mul(Div(Var('O'), Num(-1)), Sub(Var('e'), Var('N'))), Sub(Var('B'), Sub(Num(0), Var('r')))), Mul(Div(Num(2), Div(Var('b'), Add(Num(-1), Var('K')))), Add(Var('A'), Num(-1)))))))), Div(Add(Div(Sub(Sub(Mul(Num(-1), Var('N')), Mul(Div(Num(1), Div(Var('B'), Var('u'))), Div(Div(Var('i'), Var('W')), Num(-1)))), Mul(Var('h'), Var('b'))), Mul(Var('X'), Var('t'))), Var('h')), Mul(Var('g'), Add(Sub(Var('g'), Var('j')), Div(Div(Var('d'), Sub(Div(Div(Num(1), Sub(Num(0), Var('J'))), Var('s')), Div(Add(Num(-1), Var('Q')), Add(Div(Num(1), Var('b')), Add(Var('P'), Var('Q')))))), Div(Div(Sub(Add(Num(-1), Add(Var('x'), Var('x'))), Var('J')), Var('X')), Var('b')))))))), Mul(Mul(Add(Num(1), Div(Div(Add(Add(Add(Div(Sub(Num(1), Var('t')), Mul(Var('p'), Var('V'))), Mul(Add(Var('q'), Div(Var('D'), Var('M'))), Div(Num(-1), Div(Num(-1), Var('Z'))))), Sub(Add(Num(1), Add(Var('n'), Var('z'))), Sub(Div(Add(Num(1), Var('e')), Var('A')), Var('M')))), Mul(Add(Sub(Add(Mul(Var('Q'), Var('V')), Div(Var('W'), Var('u'))), Mul(Div(Var('q'), Var('q')), Sub(Var('y'), Var('y')))), Num(1)), Div(Add(Sub(Var('w'), Num(-1)), Var('f')), Sub(Num(-1), Div(Var('Y'), Var('A')))))), Sub(Div(Div(Mul(Var('S'), Sub(Num(-1), Sub(Var('T'), Num(1)))), Mul(Sub(Div(Var('W'), Var('j')), Add(Var('a'), Num(-1))), Var('V'))), Div(Mul(Mul(Div(Num(1), Var('L')), Num(-1)), Var('o')), Mul(Mul(Mul(Var('p'), Var('L')), Sub(Num(-1), Var('P'))), Num(-1)))), Mul(Sub(Div(Mul(Num(-1), Mul(Var('i'), Var('m'))), Sub(Add(Num(-1), Var('I')), Div(Var('x'), Var('h')))), Sub(Div(Num(1), Add(Var('k'), Num(-1))), Mul(Mul(Var('P'), Var('F')), Mul(Var('K'), Var('h'))))), Sub(Add(Add(Var('b'), Var('T')), Num(-2)), Mul(Add(Num(-1), Div(Var('a'), Var('u'))), Mul(Num(-1), Add(Var('y'), Var('Q')))))))), Num(-1))), Mul(Div(Div(Var('W'), Sub(Var('H'), Div(Div(Num(1), Div(Add(Mul(Var('j'), Var('M')), Var('D')), Var('A'))), Sub(Div(Var('S'), Var('P')), Var('O'))))), Var('z')), Add(Div(Div(Add(Add(Sub(Mul(Num(-1), Var('i')), Div(Num(1), Var('C'))), Num(1)), Var('v')), Sub(Mul(Add(Num(-1), Add(Var('v'), Num(-1))), Div(Num(2), Div(Num(1), Var('n')))), Add(Num(1), Var('V')))), Mul(Div(Div(Num(-1), Div(Sub(Var('M'), Var('M')), Sub(Var('B'), Var('x')))), Mul(Var('z'), Mul(Var('v'), Var('b')))), Sub(Num(0), Var('c')))), Div(Var('m'), Sub(Add(Sub(Var('D'), Sub(Var('T'), Add(Num(1), Var('e')))), Var('l')), Add(Mul(Div(Sub(Var('r'), Var('f')), Mul(Num(-1), Add(Var('Y'), Var('q')))), Mul(Div(Add(Var('B'), Var('H')), Div(Num(-1), Var('c'))), Var('I'))), Num(1))))))), Sub(Div(Add(Num(1), Div(Mul(Div(Var('h'), Mul(Add(Add(Var('E'), Var('u')), Var('L')), Var('p'))), Div(Mul(Var('J'), Add(Sub(Add(Var('j'), Num(-1)), Div(Num(1), Var('Y'))), Mul(Mul(Var('Y'), Num(-1)), Var('d')))), Div(Add(Num(-1), Var('l')), Add(Add(Num(1.0), Div(Var('D'), Num(-1))), Sub(Add(Num(1), Var('W')), Var('Z')))))), Var('y'))), Div(Add(Add(Var('d'), Mul(Div(Var('m'), Div(Sub(Var('g'), Var('i')), Num(-1.0))), Div(Mul(Div(Var('o'), Var('k')), Sub(Num(1), Var('k'))), Div(Add(Num(-1), Var('a')), Sub(Num(1), Var('B')))))), Add(Var('i'), Div(Sub(Num(0), Div(Div(Var('J'), Var('n')), Var('J'))), Sub(Div(Var('N'), Sub(Num(0), Var('B'))), Num(-2))))), Add(Mul(Add(Sub(Sub(Num(-1), Sub(Var('S'), Num(1))), Var('y')), Div(Div(Add(Var('n'), Var('M')), Num(-1)), Var('H'))), Div(Sub(Sub(Sub(Var('B'), Var('R')), Var('l')), Var('I')), Var('P'))), Num(1)))), Add(Sub(Var('I'), Add(Add(Sub(Div(Div(Num(-1), Var('A')), Var('n')), Div(Mul(Mul(Var('X'), Var('i')), Div(Var('J'), Var('H'))), Var('r'))), Num(1)), Add(Var('w'), Mul(Var('C'), Add(Sub(Num(-1), Add(Var('I'), Num(-1))), Add(Var('B'), Mul(Num(-1), Var('k')))))))), Mul(Var('Z'), Sub(Div(Mul(Num(-1), Sub(Var('u'), Div(Mul(Var('y'), Var('l')), Var('O')))), Sub(Mul(Add(Mul(Var('Y'), Num(-1)), Num(1)), Sub(Num(0), Var('a'))), Add(Var('n'), Add(Var('y'), Div(Var('E'), Num(-1)))))), Div(Mul(Sub(Add(Mul(Var('B'), Var('r')), Var('P')), Num(-1)), Sub(Num(1), Div(Var('G'), Num(-1)))), Div(Num(1), Var('j'))))))))), Mul(Div(Sub(Add(Var('U'), Sub(Sub(Mul(Add(Div(Num(1), Div(Var('l'), Num(-1))), Add(Var('W'), Num(-1))), Sub(Mul(Div(Mul(Var('y'), Var('e')), Div(Var('C'), Var('L'))), Div(Add(Num(1), Var('p')), Mul(Var('G'), Num(-1)))), Sub(Var('X'), Div(Sub(Var('E'), Var('r')), Add(Var('F'), Var('X')))))), Add(Div(Mul(Var('L'), Add(Div(Var('V'), Num(-1)), Num(1))), Div(Mul(Var('R'), Sub(Var('w'), Var('T'))), Mul(Sub(Var('b'), Var('q')), Div(Var('G'), Num(-1))))), Mul(Sub(Num(-1.0), Sub(Div(Var('d'), Var('y')), Sub(Num(1), Var('d')))), Sub(Var('q'), Num(1))))), Num(-1))), Sub(Num(0), Div(Num(-1), Mul(Sub(Div(Num(-1), Sub(Var('U'), Var('g'))), Var('B')), Num(-1))))), Mul(Add(Mul(Add(Div(Mul(Add(Sub(Var('r'), Var('E')), Div(Div(Var('N'), Num(-1)), Div(Var('X'), Var('S')))), Add(Add(Num(-1), Div(Num(-1), Var('W'))), Sub(Var('Z'), Var('P')))), Div(Sub(Sub(Var('Q'), Num(-1)), Mul(Var('l'), Add(Var('n'), Var('t')))), Add(Mul(Sub(Var('X'), Num(-1)), Div(Num(-1), Var('p'))), Num(1)))), Add(Add(Var('M'), Sub(Sub(Num(-1), Mul(Var('V'), Var('N'))), Num(1))), Sub(Var('D'), Sub(Sub(Var('T'), Var('Y')), Add(Mul(Var('a'), Num(-1)), Var('V')))))), Add(Var('I'), Add(Sub(Mul(Add(Mul(Var('V'), Num(-1)), Num(1.0)), Div(Div(Var('M'), Var('E')), Var('D'))), Num(1)), Sub(Num(-1), Div(Add(Div(Num(1), Var('o')), Div(Num(1), Var('n'))), Div(Num(1), Mul(Var('W'), Num(-1)))))))), Num(-1)), Num(-1))), Mul(Add(Sub(Div(Sub(Var('M'), Mul(Var('x'), Div(Var('l'), Add(Mul(Div(Add(Num(1), Var('T')), Sub(Var('N'), Var('q'))), Sub(Div(Num(-1), Var('T')), Var('T'))), Div(Sub(Var('L'), Sub(Num(0), Var('q'))), Mul(Var('w'), Add(Var('f'), Num(-1)))))))), Sub(Sub(Div(Sub(Num(0), Mul(Sub(Add(Var('k'), Num(1)), Div(Var('N'), Num(-1))), Add(Num(1), Mul(Num(-1), Var('I'))))), Add(Div(Sub(Var('t'), Var('h')), Mul(Var('i'), Var('Y'))), Var('W'))), Sub(Var('b'), Num(-1))), Add(Add(Div(Num(-1), Sub(Var('n'), Num(-1))), Div(Div(Num(-1), Var('D')), Num(-1))), Mul(Sub(Num(-1), Sub(Div(Var('i'), Num(-1)), Div(Div(Var('F'), Var('m')), Div(Var('x'), Num(-1))))), Add(Var('L'), Sub(Add(Add(Var('B'), Var('W')), Mul(Num(-1), Var('c'))), Num(1))))))), Mul(Add(Add(Add(Sub(Var('H'), Sub(Sub(Var('b'), Num(1)), Sub(Sub(Var('R'), Var('B')), Num(1)))), Var('T')), Num(-1)), Var('I')), Sub(Add(Div(Mul(Add(Var('s'), Add(Var('V'), Var('a'))), Var('K')), Add(Mul(Var('V'), Var('m')), Add(Num(-1), Add(Sub(Num(-1), Var('e')), Num(-1))))), Mul(Mul(Add(Var('W'), Sub(Mul(Var('v'), Var('k')), Var('Y'))), Div(Var('B'), Mul(Div(Num(1), Var('y')), Num(-1)))), Var('z'))), Add(Var('I'), Div(Add(Sub(Var('x'), Num(-1)), Add(Var('Q'), Add(Div(Var('u'), Var('o')), Add(Var('D'), Var('V'))))), Add(Var('e'), Num(1))))))), Mul(Sub(Add(Mul(Mul(Add(Sub(Add(Mul(Var('T'), Var('R')), Div(Num(1), Var('q'))), Sub(Var('O'), Div(Num(-1), Var('F')))), Var('Y')), Num(-1)), Mul(Var('N'), Var('S'))), Var('x')), Var('A')), Var('O'))), Mul(Add(Sub(Add(Add(Div(Mul(Var('D'), Var('X')), Add(Div(Var('X'), Add(Var('V'), Num(-1))), Sub(Div(Var('q'), Var('L')), Div(Div(Var('S'), Num(-1)), Mul(Var('e'), Num(-1)))))), Add(Add(Div(Sub(Num(-1), Var('H')), Mul(Mul(Var('b'), Num(-1)), Sub(Num(-1), Var('j')))), Mul(Sub(Sub(Var('p'), Var('j')), Sub(Num(0), Var('S'))), Sub(Mul(Num(-1), Var('s')), Add(Var('d'), Var('z'))))), Sub(Mul(Num(-1), Sub(Mul(Num(-1), Var('r')), Div(Num(1), Var('V')))), Sub(Div(Var('F'), Div(Var('m'), Num(-1))), Div(Add(Num(-1), Var('Z')), Var('X')))))), Var('x')), Mul(Div(Div(Add(Mul(Div(Div(Var('K'), Var('v')), Div(Var('M'), Var('s'))), Sub(Sub(Var('a'), Var('A')), Var('A'))), Num(-1)), Add(Div(Num(2), Sub(Var('m'), Var('T'))), Sub(Sub(Add(Num(-1), Var('K')), Num(2)), Num(1)))), Num(-1)), Div(Num(1), Div(Div(Var('a'), Num(-1)), Add(Add(Sub(Div(Var('r'), Var('j')), Sub(Var('R'), Num(-1))), Sub(Var('n'), Var('Q'))), Div(Div(Sub(Var('y'), Var('P')), Sub(Var('i'), Var('Q'))), Sub(Var('m'), Div(Var('n'), Var('J'))))))))), Mul(Num(-1), Var('d'))), Sub(Sub(Sub(Num(0), Sub(Mul(Mul(Add(Add(Var('r'), Num(-1)), Var('J')), Sub(Num(-1), Mul(Num(-1), Var('S')))), Add(Add(Add(Sub(Var('C'), Var('V')), Var('p')), Mul(Var('Y'), Var('M'))), Add(Var('C'), Add(Mul(Var('T'), Var('M')), Add(Var('O'), Var('y')))))), Sub(Var('y'), Sub(Sub(Var('O'), Div(Sub(Var('f'), Var('j')), Add(Var('P'), Num(-1)))), Add(Div(Var('W'), Var('T')), Div(Var('b'), Num(-1))))))), Num(-1)), Mul(Mul(Sub(Num(0), Mul(Add(Div(Div(Var('O'), Var('h')), Var('U')), Sub(Add(Sub(Num(1), Var('R')), Var('G')), Num(-1))), Div(Add(Mul(Div(Var('J'), Var('q')), Div(Var('G'), Var('p'))), Mul(Div(Num(1), Var('D')), Var('d'))), Mul(Div(Div(Num(1), Var('I')), Sub(Num(1), Var('C'))), Var('d'))))), Mul(Div(Var('e'), Var('V')), Add(Mul(Mul(Mul(Sub(Var('G'), Var('q')), Num(-1)), Var('M')), Div(Mul(Sub(Num(0), Var('Z')), Add(Var('b'), Var('X'))), Div(Var('K'), Div(Var('F'), Var('d'))))), Div(Sub(Var('l'), Div(Num(1), Var('D'))), Mul(Var('s'), Sub(Var('Y'), Var('u'))))))), Sub(Var('Z'), Var('O'))))))))))
    #result=Sub(Num(1), Mul(Mul(Num(-1), Div(Div(Sub(Sub(Sub(Sub(Sub(Mul(Div(Add(Add(Sub(Num(1), Var('j')), Var('o')), Var('c')), Add(Add(Div(Var('l'), Var('u')), Add(Num(0), Var('X'))), Div(Sub(Var('g'), Num(1)), Sub(Var('B'), Var('T'))))), Add(Sub(Add(Mul(Var('b'), Num(1)), Sub(Num(0), Num(0))), Num(0)), Var('a'))), Add(Mul(Num(-1), Sub(Mul(Num(-1), Div(Var('s'), Var('L'))), Sub(Sub(Var('b'), Num(-1)), Div(Var('P'), Var('X'))))), Mul(Add(Var('I'), Var('N')), Var('G')))), Add(Sub(Var('s'), Mul(Add(Add(Mul(Num(0), Num(-1)), Add(Var('u'), Var('H'))), Mul(Sub(Num(1), Var('l')), Div(Num(-1), Var('B')))), Var('A'))), Mul(Div(Add(Sub(Var('T'), Num(1)), Num(-1)), Num(-1)), Mul(Div(Var('O'), Add(Add(Var('b'), Var('Q')), Sub(Var('j'), Num(0)))), Sub(Var('L'), Mul(Num(0), Num(1))))))), Var('q')), Sub(Div(Num(1), Add(Var('e'), Sub(Add(Var('Y'), Sub(Add(Div(Num(0), Num(1)), Div(Var('e'), Num(1))), Sub(Sub(Var('Z'), Var('v')), Add(Var('P'), Var('M'))))), Add(Add(Add(Div(Num(0), Var('i')), Num(1)), Sub(Var('U'), Mul(Num(1), Num(-1)))), Mul(Add(Div(Num(1), Var('m')), Mul(Var('e'), Var('M'))), Var('U')))))), Var('c'))), Num(-1)), Add(Div(Var('v'), Div(Add(Num(0), Var('D')), Num(-1))), Mul(Sub(Add(Sub(Var('M'), Sub(Div(Var('f'), Mul(Sub(Var('w'), Num(0)), Var('P'))), Div(Mul(Num(1), Div(Var('p'), Var('T'))), Add(Add(Sub(Num(-1), Var('B')), Var('u')), Div(Sub(Var('i'), Var('r')), Sub(Var('e'), Num(-1))))))), Sub(Sub(Mul(Add(Mul(Div(Var('y'), Var('E')), Num(0)), Sub(Add(Num(1), Num(1)), Sub(Var('G'), Num(0)))), Num(1)), Mul(Var('Z'), Sub(Mul(Mul(Var('u'), Num(-1)), Add(Num(1), Num(1))), Mul(Mul(Var('z'), Var('N')), Num(1))))), Div(Num(0), Num(-1)))), Add(Div(Num(0), Num(-1)), Div(Mul(Add(Mul(Sub(Mul(Num(1), Num(-1)), Mul(Var('O'), Num(0))), Sub(Var('q'), Var('I'))), Add(Sub(Sub(Var('l'), Var('V')), Sub(Var('F'), Var('g'))), Add(Num(1), Div(Var('k'), Num(1))))), Var('e')), Div(Mul(Mul(Div(Div(Var('w'), Num(1)), Var('V')), Sub(Div(Num(0), Var('N')), Sub(Var('s'), Num(0)))), Add(Add(Mul(Num(0), Num(1)), Var('Y')), Sub(Num(-1), Add(Var('G'), Var('R'))))), Sub(Var('t'), Add(Add(Num(-1), Add(Num(1), Var('c'))), Mul(Div(Var('E'), Var('i')), Num(-1)))))))), Var('L')))), Num(-1))), Sub(Div(Mul(Add(Mul(Add(Mul(Div(Sub(Div(Div(Var('a'), Div(Add(Var('K'), Num(0)), Mul(Var('i'), Num(-1)))), Add(Add(Var('m'), Mul(Num(1), Var('A'))), Mul(Num(0), Sub(Var('P'), Num(1))))), Mul(Var('L'), Div(Mul(Div(Num(1), Var('Y')), Div(Var('O'), Var('x'))), Div(Mul(Var('U'), Num(-1)), Sub(Var('Z'), Num(1)))))), Sub(Var('H'), Mul(Mul(Div(Sub(Var('F'), Var('U')), Num(1)), Add(Var('I'), Div(Num(-1), Var('S')))), Mul(Num(1), Div(Var('g'), Num(-1)))))), Mul(Mul(Sub(Var('p'), Sub(Num(1), Var('G'))), Num(0)), Num(0))), Mul(Div(Div(Sub(Add(Add(Sub(Var('I'), Num(1)), Div(Num(1), Var('Q'))), Sub(Div(Var('G'), Num(1)), Num(-1))), Var('J')), Var('c')), Mul(Num(-1), Div(Sub(Num(-1), Mul(Num(1), Mul(Num(0), Num(0)))), Div(Sub(Mul(Num(1), Var('E')), Div(Var('E'), Var('l'))), Add(Div(Var('h'), Num(-1)), Add(Var('V'), Num(-1))))))), Var('E'))), Add(Mul(Mul(Var('C'), Div(Sub(Div(Var('R'), Var('t')), Div(Add(Div(Var('n'), Num(1)), Div(Num(1), Num(-1))), Num(-1))), Mul(Num(-1), Num(-1)))), Num(0)), Mul(Div(Add(Mul(Mul(Mul(Sub(Var('X'), Num(-1)), Mul(Num(1), Var('v'))), Num(0)), Var('P')), Var('k')), Mul(Div(Add(Var('d'), Var('A')), Add(Mul(Mul(Num(-1), Var('r')), Div(Num(1), Var('D'))), Num(-1))), Sub(Add(Div(Var('A'), Var('Z')), Add(Add(Var('L'), Num(0)), Div(Var('T'), Num(1)))), Div(Div(Add(Num(1), Var('b')), Div(Num(-1), Num(1))), Div(Mul(Var('I'), Var('n')), Add(Var('B'), Var('E'))))))), Div(Add(Mul(Add(Add(Add(Num(1), Num(0)), Sub(Num(1), Num(0))), Mul(Div(Num(-1), Var('S')), Sub(Var('E'), Var('d')))), Add(Mul(Var('F'), Add(Var('n'), Var('n'))), Sub(Num(-1), Div(Var('I'), Num(1))))), Div(Add(Num(1), Var('e')), Num(1))), Var('Y'))))), Var('x')), Sub(Sub(Mul(Sub(Add(Div(Num(0), Var('D')), Add(Mul(Num(0), Mul(Sub(Num(1), Sub(Var('L'), Var('C'))), Div(Mul(Num(1), Num(0)), Add(Num(0), Num(-1))))), Sub(Mul(Div(Mul(Var('H'), Num(1)), Div(Var('O'), Num(-1))), Mul(Var('t'), Num(0))), Mul(Sub(Mul(Var('j'), Num(0)), Var('E')), Add(Var('J'), Num(1)))))), Var('P')), Sub(Sub(Div(Sub(Mul(Sub(Sub(Var('P'), Var('t')), Var('V')), Num(-1)), Div(Sub(Sub(Var('o'), Num(0)), Div(Num(1), Var('m'))), Num(1))), Sub(Sub(Mul(Add(Num(0), Num(-1)), Div(Var('f'), Var('e'))), Div(Mul(Var('f'), Num(-1)), Div(Var('X'), Var('J')))), Mul(Mul(Mul(Var('G'), Var('n')), Sub(Var('O'), Var('y'))), Num(1)))), Div(Num(-1), Mul(Num(1), Num(1)))), Add(Add(Mul(Sub(Div(Add(Num(-1), Num(1)), Var('D')), Mul(Add(Var('q'), Var('f')), Mul(Num(0), Var('D')))), Add(Div(Add(Num(1), Var('m')), Num(-1)), Var('i'))), Var('Z')), Div(Mul(Mul(Num(1), Num(0)), Div(Div(Mul(Num(-1), Var('N')), Add(Num(-1), Num(-1))), Sub(Mul(Var('k'), Num(0)), Div(Var('x'), Var('L'))))), Num(1))))), Sub(Num(1), Div(Add(Num(-1), Var('F')), Sub(Sub(Mul(Var('g'), Num(0)), Num(-1)), Sub(Mul(Num(1), Mul(Mul(Div(Var('O'), Num(-1)), Sub(Var('e'), Var('N'))), Sub(Mul(Num(1), Var('B')), Sub(Num(0), Var('r'))))), Mul(Div(Add(Num(1), Num(1)), Div(Sub(Var('b'), Num(0)), Add(Num(-1), Var('K')))), Add(Var('A'), Num(-1)))))))), Div(Mul(Num(1), Add(Div(Sub(Sub(Add(Sub(Mul(Num(-1), Var('N')), Mul(Var('a'), Num(0))), Mul(Sub(Var('d'), Num(1)), Num(0))), Mul(Div(Mul(Num(-1), Num(-1)), Div(Var('B'), Var('u'))), Div(Div(Var('i'), Var('W')), Sub(Num(0), Num(1))))), Mul(Var('h'), Var('b'))), Mul(Var('X'), Var('t'))), Var('h'))), Mul(Var('g'), Add(Add(Div(Mul(Add(Sub(Num(-1), Mul(Var('f'), Var('D'))), Mul(Div(Var('W'), Var('M')), Num(0))), Num(0)), Var('m')), Sub(Var('g'), Var('j'))), Div(Div(Var('d'), Sub(Div(Div(Num(1), Sub(Num(0), Var('J'))), Var('s')), Div(Mul(Mul(Num(1), Num(1)), Add(Num(-1), Var('Q'))), Add(Div(Num(1), Var('b')), Add(Var('P'), Var('Q')))))), Div(Div(Sub(Add(Num(-1), Add(Var('x'), Var('x'))), Var('J')), Mul(Var('X'), Num(1))), Var('b')))))))), Mul(Mul(Add(Num(1), Div(Div(Add(Add(Add(Div(Sub(Num(1), Add(Num(0), Var('t'))), Add(Div(Num(0), Var('s')), Mul(Var('p'), Var('V')))), Mul(Add(Sub(Var('q'), Num(0)), Div(Var('D'), Var('M'))), Div(Div(Num(-1), Num(1)), Div(Num(-1), Var('Z'))))), Sub(Add(Num(1), Mul(Add(Var('n'), Var('z')), Add(Num(0), Num(1)))), Sub(Div(Add(Num(1), Var('e')), Var('A')), Var('M')))), Mul(Add(Sub(Add(Mul(Var('Q'), Var('V')), Div(Var('W'), Var('u'))), Mul(Div(Var('q'), Var('q')), Sub(Var('y'), Var('y')))), Sub(Num(0), Num(-1))), Add(Mul(Mul(Add(Num(-1), Var('m')), Sub(Var('Z'), Num(1))), Mul(Sub(Num(0), Num(0)), Div(Var('V'), Var('n')))), Div(Add(Sub(Var('w'), Num(-1)), Var('f')), Sub(Add(Num(0), Num(-1)), Div(Var('Y'), Var('A'))))))), Sub(Div(Div(Mul(Var('S'), Sub(Sub(Num(-1), Num(0)), Sub(Var('T'), Num(1)))), Mul(Sub(Div(Var('W'), Var('j')), Add(Var('a'), Num(-1))), Var('V'))), Div(Mul(Mul(Div(Num(1), Var('L')), Sub(Num(0), Num(1))), Var('o')), Mul(Mul(Mul(Var('p'), Var('L')), Sub(Num(-1), Var('P'))), Div(Sub(Num(-1), Num(0)), Num(1))))), Mul(Sub(Div(Mul(Num(-1), Mul(Var('i'), Var('m'))), Sub(Add(Num(-1), Var('I')), Div(Var('x'), Var('h')))), Sub(Div(Num(1), Add(Var('k'), Num(-1))), Mul(Mul(Var('P'), Var('F')), Mul(Var('K'), Var('h'))))), Sub(Add(Div(Add(Var('b'), Var('T')), Mul(Num(-1), Num(-1))), Mul(Add(Num(1), Num(1)), Num(-1))), Mul(Add(Sub(Num(0), Num(1)), Div(Var('a'), Var('u'))), Mul(Div(Num(-1), Num(1)), Add(Var('y'), Var('Q')))))))), Sub(Num(0), Num(1)))), Mul(Div(Div(Var('W'), Sub(Div(Var('H'), Num(1)), Div(Div(Num(1), Div(Add(Mul(Var('j'), Var('M')), Var('D')), Var('A'))), Sub(Div(Var('S'), Var('P')), Var('O'))))), Var('z')), Add(Add(Div(Div(Add(Add(Sub(Mul(Num(-1), Var('i')), Div(Num(1), Var('C'))), Num(1)), Var('v')), Sub(Mul(Add(Mul(Num(-1), Num(1)), Add(Var('v'), Num(-1))), Div(Add(Num(1), Num(1)), Div(Num(1), Var('n')))), Add(Num(1), Sub(Var('V'), Num(0))))), Mul(Div(Div(Mul(Num(1), Sub(Num(0), Num(1))), Div(Sub(Var('M'), Var('M')), Sub(Var('B'), Var('x')))), Add(Mul(Var('z'), Mul(Var('v'), Var('b'))), Div(Num(0), Add(Var('r'), Var('p'))))), Sub(Mul(Div(Mul(Num(-1), Var('B')), Sub(Var('R'), Num(1))), Mul(Sub(Num(0), Num(1)), Sub(Num(-1), Num(-1)))), Var('c')))), Mul(Num(0), Mul(Add(Sub(Div(Mul(Num(1), Num(1)), Div(Num(-1), Num(1))), Mul(Add(Num(0), Var('r')), Sub(Num(-1), Var('Q')))), Var('w')), Mul(Var('C'), Var('V'))))), Div(Var('m'), Sub(Sub(Add(Sub(Var('D'), Sub(Var('T'), Add(Num(1), Var('e')))), Var('l')), Mul(Num(0), Sub(Mul(Num(1), Mul(Var('A'), Var('F'))), Sub(Num(0), Mul(Var('n'), Num(0)))))), Add(Mul(Div(Sub(Sub(Var('r'), Num(0)), Var('f')), Mul(Num(-1), Add(Var('Y'), Var('q')))), Mul(Div(Add(Var('B'), Var('H')), Div(Num(-1), Var('c'))), Var('I'))), Num(1))))))), Sub(Div(Add(Num(1), Div(Mul(Div(Var('h'), Mul(Add(Add(Add(Var('E'), Num(0)), Var('u')), Var('L')), Var('p'))), Div(Mul(Var('J'), Add(Sub(Add(Var('j'), Num(-1)), Div(Num(1), Var('Y'))), Mul(Mul(Var('Y'), Num(-1)), Var('d')))), Div(Mul(Add(Num(0), Add(Num(-1), Var('l'))), Sub(Div(Num(0), Num(1)), Num(-1))), Add(Add(Div(Num(-1), Num(-1)), Div(Var('D'), Num(-1))), Sub(Add(Num(1), Var('W')), Div(Var('Z'), Num(1))))))), Var('y'))), Div(Div(Add(Add(Var('d'), Mul(Div(Add(Sub(Var('m'), Num(0)), Div(Num(0), Num(-1))), Div(Sub(Var('g'), Var('i')), Div(Num(1), Num(-1)))), Div(Mul(Div(Var('o'), Var('k')), Sub(Num(1), Var('k'))), Div(Add(Num(-1), Var('a')), Sub(Num(1), Var('B')))))), Add(Var('i'), Div(Sub(Div(Add(Num(1), Num(-1)), Sub(Var('u'), Var('N'))), Div(Div(Var('J'), Var('n')), Var('J'))), Sub(Div(Mul(Num(1), Var('N')), Sub(Num(0), Var('B'))), Mul(Add(Num(-1), Num(-1)), Div(Num(-1), Num(-1))))))), Mul(Num(-1), Num(-1))), Sub(Add(Mul(Add(Sub(Sub(Num(-1), Sub(Var('S'), Num(1))), Mul(Add(Num(0), Var('y')), Num(1))), Div(Div(Add(Var('n'), Var('M')), Sub(Num(-1), Num(0))), Var('H'))), Div(Sub(Sub(Sub(Var('B'), Var('R')), Var('l')), Var('I')), Var('P'))), Add(Num(1), Mul(Var('k'), Mul(Mul(Mul(Num(0), Num(1)), Mul(Var('s'), Num(0))), Num(0))))), Mul(Div(Num(1), Num(1)), Num(0))))), Add(Mul(Mul(Add(Mul(Mul(Div(Div(Sub(Var('l'), Var('b')), Add(Var('E'), Num(0))), Sub(Mul(Var('n'), Num(0)), Var('K'))), Sub(Mul(Mul(Var('n'), Var('I')), Add(Var('n'), Num(0))), Num(-1))), Mul(Num(1), Num(0))), Add(Div(Num(0), Sub(Mul(Sub(Num(0), Num(-1)), Mul(Var('I'), Num(0))), Add(Div(Var('m'), Num(1)), Div(Var('x'), Var('s'))))), Mul(Mul(Sub(Add(Num(1), Num(-1)), Var('R')), Num(0)), Div(Add(Sub(Num(1), Num(0)), Add(Var('L'), Num(0))), Sub(Num(1), Sub(Num(-1), Var('G'))))))), Mul(Div(Sub(Div(Sub(Div(Num(-1), Var('D')), Sub(Num(-1), Var('i'))), Num(-1)), Mul(Add(Sub(Var('l'), Var('t')), Sub(Num(-1), Var('i'))), Mul(Sub(Var('n'), Var('w')), Add(Var('f'), Num(1))))), Div(Var('V'), Sub(Var('c'), Num(-1)))), Num(1))), Num(1)), Add(Sub(Var('I'), Add(Add(Sub(Div(Div(Num(-1), Var('A')), Var('n')), Div(Mul(Mul(Var('X'), Var('i')), Div(Var('J'), Var('H'))), Sub(Add(Num(0), Var('r')), Sub(Num(-1), Num(-1))))), Num(1)), Add(Var('w'), Mul(Var('C'), Add(Sub(Num(-1), Add(Var('I'), Num(-1))), Add(Var('B'), Mul(Num(-1), Var('k')))))))), Mul(Var('Z'), Sub(Div(Mul(Num(-1), Sub(Var('u'), Div(Mul(Var('y'), Var('l')), Var('O')))), Sub(Mul(Add(Mul(Var('Y'), Num(-1)), Add(Num(1), Num(0))), Sub(Add(Num(-1), Num(1)), Var('a'))), Add(Var('n'), Add(Div(Var('y'), Num(1)), Div(Var('E'), Num(-1)))))), Div(Mul(Sub(Add(Mul(Var('B'), Var('r')), Sub(Var('P'), Num(0))), Num(-1)), Sub(Num(1), Div(Sub(Var('G'), Num(0)), Num(-1)))), Div(Sub(Add(Add(Num(-1), Num(1)), Add(Num(1), Num(-1))), Num(-1)), Var('j')))))))))), Mul(Add(Div(Sub(Add(Var('U'), Sub(Sub(Mul(Add(Mul(Div(Sub(Num(0), Num(1)), Num(-1)), Div(Mul(Num(1), Num(1)), Div(Var('l'), Num(-1)))), Add(Var('W'), Num(-1))), Sub(Mul(Div(Mul(Var('y'), Var('e')), Div(Var('C'), Var('L'))), Div(Add(Num(1), Var('p')), Mul(Var('G'), Num(-1)))), Sub(Var('X'), Div(Sub(Var('E'), Var('r')), Add(Var('F'), Var('X')))))), Add(Div(Mul(Var('L'), Add(Div(Var('V'), Num(-1)), Num(1))), Div(Mul(Add(Var('R'), Num(0)), Sub(Var('w'), Var('T'))), Mul(Sub(Var('b'), Var('q')), Div(Var('G'), Num(-1))))), Mul(Sub(Div(Div(Num(1), Num(-1)), Num(1)), Sub(Div(Var('d'), Var('y')), Sub(Num(1), Var('d')))), Sub(Var('q'), Num(1))))), Num(-1))), Sub(Num(0), Div(Num(-1), Mul(Sub(Add(Sub(Div(Div(Num(-1), Num(1)), Sub(Var('U'), Var('g'))), Var('B')), Div(Div(Div(Num(0), Var('e')), Sub(Var('B'), Num(0))), Add(Num(-1), Num(-1)))), Mul(Num(0), Var('N'))), Sub(Mul(Var('o'), Num(0)), Num(1)))))), Mul(Add(Mul(Add(Div(Mul(Add(Add(Sub(Var('r'), Var('E')), Num(0)), Div(Div(Var('N'), Num(-1)), Div(Var('X'), Var('S')))), Add(Add(Num(-1), Div(Num(-1), Var('W'))), Sub(Var('Z'), Var('P')))), Div(Sub(Sub(Mul(Var('Q'), Num(1)), Add(Num(0), Num(-1))), Mul(Mul(Num(1), Var('l')), Add(Var('n'), Var('t')))), Add(Mul(Sub(Var('X'), Num(-1)), Div(Num(-1), Var('p'))), Num(1)))), Add(Add(Var('M'), Sub(Sub(Add(Num(0), Num(-1)), Mul(Var('V'), Var('N'))), Num(1))), Sub(Sub(Var('D'), Mul(Div(Var('R'), Var('B')), Num(0))), Sub(Sub(Var('T'), Var('Y')), Add(Mul(Var('a'), Num(-1)), Var('V')))))), Add(Var('I'), Add(Sub(Mul(Add(Mul(Var('V'), Num(-1)), Div(Num(-1), Num(-1))), Div(Div(Var('M'), Var('E')), Var('D'))), Num(1)), Sub(Div(Num(-1), Num(1)), Div(Add(Div(Num(1), Var('o')), Div(Num(1), Var('n'))), Div(Num(1), Mul(Var('W'), Num(-1)))))))), Num(-1)), Num(-1))), Add(Div(Num(0), Div(Sub(Div(Mul(Mul(Sub(Mul(Sub(Num(0), Var('L')), Var('Q')), Sub(Div(Num(1), Num(1)), Div(Var('E'), Num(1)))), Add(Div(Add(Var('V'), Var('g')), Div(Var('o'), Num(1))), Add(Div(Var('q'), Num(-1)), Sub(Var('N'), Num(-1))))), Sub(Add(Sub(Sub(Num(0), Num(1)), Sub(Var('X'), Var('o'))), Div(Mul(Var('Y'), Var('e')), Add(Num(0), Var('q')))), Sub(Div(Var('W'), Div(Var('I'), Num(-1))), Add(Mul(Var('Z'), Num(-1)), Add(Num(1), Var('v')))))), Sub(Sub(Num(-1), Sub(Num(0), Num(-1))), Mul(Num(0), Div(Mul(Div(Var('f'), Var('D')), Sub(Num(0), Var('Z'))), Sub(Add(Num(1), Num(1)), Sub(Var('x'), Var('k'))))))), Add(Sub(Add(Add(Mul(Div(Var('V'), Var('u')), Sub(Num(1), Var('n'))), Add(Sub(Var('Y'), Var('o')), Add(Num(-1), Num(0)))), Mul(Div(Num(1), Div(Var('Q'), Num(1))), Div(Var('s'), Div(Var('z'), Var('P'))))), Add(Var('N'), Var('i'))), Sub(Sub(Div(Sub(Div(Num(0), Var('k')), Var('K')), Var('q')), Sub(Div(Var('X'), Add(Num(0), Var('z'))), Num(-1))), Var('B')))), Mul(Num(1), Div(Sub(Sub(Div(Num(1), Sub(Div(Num(-1), Num(-1)), Sub(Num(-1), Num(-1)))), Div(Sub(Sub(Var('j'), Num(-1)), Div(Var('m'), Var('w'))), Div(Add(Num(0), Var('Q')), Add(Var('e'), Num(1))))), Sub(Sub(Add(Sub(Var('a'), Var('z')), Div(Num(-1), Num(-1))), Sub(Num(-1), Div(Var('N'), Num(-1)))), Mul(Sub(Add(Var('n'), Num(0)), Mul(Num(1), Num(1))), Mul(Num(0), Div(Num(-1), Var('B')))))), Add(Mul(Var('V'), Add(Sub(Add(Var('T'), Num(0)), Div(Var('p'), Var('F'))), Var('Y'))), Add(Div(Mul(Num(1), Sub(Num(0), Num(-1))), Var('z')), Mul(Div(Div(Num(0), Var('y')), Add(Num(-1), Num(0))), Div(Add(Num(0), Var('h')), Add(Var('v'), Num(-1)))))))))), Num(0))), Mul(Add(Sub(Div(Sub(Var('M'), Mul(Var('x'), Div(Var('l'), Add(Mul(Div(Add(Num(1), Var('T')), Sub(Var('N'), Var('q'))), Sub(Div(Num(-1), Var('T')), Add(Num(0), Var('T')))), Div(Sub(Add(Num(0), Var('L')), Sub(Num(0), Var('q'))), Mul(Div(Var('w'), Num(1)), Add(Var('f'), Num(-1)))))))), Sub(Sub(Div(Sub(Num(0), Mul(Sub(Add(Var('k'), Num(1)), Div(Var('N'), Num(-1))), Add(Mul(Num(1), Num(1)), Mul(Num(-1), Var('I'))))), Mul(Num(1), Add(Div(Sub(Var('t'), Var('h')), Mul(Var('i'), Var('Y'))), Mul(Mul(Var('W'), Num(1)), Num(1))))), Sub(Var('b'), Num(-1))), Add(Add(Div(Num(-1), Sub(Sub(Var('n'), Add(Num(0), Num(-1))), Sub(Mul(Num(-1), Num(0)), Div(Num(0), Var('V'))))), Add(Mul(Sub(Add(Num(0), Var('U')), Div(Var('D'), Var('d'))), Num(0)), Div(Div(Num(-1), Mul(Var('D'), Num(1))), Num(-1)))), Mul(Sub(Num(-1), Sub(Add(Div(Var('i'), Num(-1)), Mul(Num(0), Var('v'))), Div(Div(Var('F'), Var('m')), Div(Var('x'), Num(-1))))), Add(Var('L'), Sub(Add(Add(Var('B'), Var('W')), Mul(Num(-1), Var('c'))), Num(1))))))), Mul(Add(Add(Add(Sub(Mul(Var('H'), Num(1)), Sub(Sub(Mul(Var('b'), Num(1)), Div(Num(1), Num(1))), Sub(Sub(Var('R'), Var('B')), Mul(Num(1), Num(1))))), Var('T')), Num(-1)), Var('I')), Sub(Add(Div(Add(Mul(Div(Var('U'), Div(Var('t'), Var('l'))), Mul(Mul(Num(0), Var('D')), Sub(Var('i'), Num(0)))), Mul(Add(Var('s'), Add(Var('V'), Var('a'))), Var('K'))), Add(Add(Mul(Var('V'), Var('m')), Div(Div(Num(0), Num(-1)), Div(Num(-1), Var('u')))), Add(Num(-1), Add(Sub(Num(-1), Var('e')), Num(-1))))), Mul(Mul(Add(Var('W'), Sub(Mul(Var('v'), Var('k')), Sub(Var('Y'), Num(0)))), Div(Mul(Var('B'), Sub(Num(0), Num(-1))), Mul(Div(Num(1), Var('y')), Num(-1)))), Sub(Add(Var('z'), Sub(Mul(Var('Q'), Num(0)), Div(Num(0), Num(1)))), Num(0)))), Add(Var('I'), Div(Add(Sub(Var('x'), Num(-1)), Add(Var('Q'), Add(Div(Var('u'), Var('o')), Add(Var('D'), Var('V'))))), Add(Var('e'), Num(1))))))), Mul(Sub(Add(Mul(Mul(Add(Sub(Add(Mul(Var('T'), Var('R')), Div(Num(1), Var('q'))), Sub(Var('O'), Div(Num(-1), Var('F')))), Var('Y')), Num(-1)), Mul(Var('N'), Sub(Var('S'), Num(0)))), Var('x')), Var('A')), Var('O'))), Mul(Add(Sub(Add(Add(Div(Mul(Add(Var('D'), Div(Div(Num(0), Num(-1)), Div(Num(1), Var('m')))), Var('X')), Add(Div(Var('X'), Add(Add(Num(0), Num(0)), Add(Var('V'), Num(-1)))), Sub(Mul(Div(Var('q'), Var('L')), Num(1)), Div(Div(Var('S'), Num(-1)), Mul(Var('e'), Num(-1)))))), Add(Add(Div(Sub(Mul(Num(-1), Num(1)), Var('H')), Mul(Mul(Var('b'), Num(-1)), Sub(Num(-1), Var('j')))), Mul(Sub(Sub(Var('p'), Var('j')), Sub(Num(0), Var('S'))), Sub(Mul(Num(-1), Var('s')), Add(Var('d'), Var('z'))))), Sub(Mul(Num(-1), Sub(Mul(Num(-1), Var('r')), Div(Num(1), Var('V')))), Sub(Div(Div(Var('F'), Num(1)), Div(Var('m'), Num(-1))), Div(Add(Num(-1), Var('Z')), Mul(Var('X'), Num(1))))))), Var('x')), Mul(Div(Div(Add(Mul(Div(Div(Var('K'), Var('v')), Div(Var('M'), Var('s'))), Sub(Sub(Var('a'), Var('A')), Var('A'))), Num(-1)), Add(Div(Sub(Mul(Num(1), Num(1)), Num(-1)), Sub(Sub(Var('m'), Var('T')), Add(Num(1), Num(-1)))), Sub(Sub(Add(Num(-1), Var('K')), Sub(Num(1), Num(-1))), Num(1)))), Num(-1)), Div(Add(Mul(Num(1), Mul(Mul(Num(-1), Mul(Num(0), Var('t'))), Add(Mul(Var('s'), Var('U')), Add(Var('p'), Num(-1))))), Num(1)), Div(Div(Var('a'), Num(-1)), Add(Add(Sub(Div(Var('r'), Var('j')), Sub(Var('R'), Num(-1))), Sub(Var('n'), Add(Var('Q'), Num(0)))), Div(Div(Sub(Var('y'), Var('P')), Sub(Var('i'), Var('Q'))), Sub(Add(Num(0), Var('m')), Div(Var('n'), Var('J'))))))))), Mul(Num(-1), Add(Var('d'), Div(Num(0), Div(Num(-1), Add(Sub(Var('I'), Add(Var('c'), Div(Num(0), Num(-1)))), Div(Div(Div(Var('v'), Var('A')), Sub(Num(0), Num(-1))), Div(Mul(Var('b'), Num(1)), Mul(Var('S'), Num(1)))))))))), Sub(Sub(Sub(Div(Div(Div(Mul(Div(Mul(Num(0), Var('r')), Sub(Var('C'), Var('G'))), Div(Sub(Var('O'), Num(-1)), Add(Num(1), Var('q')))), Add(Div(Mul(Num(-1), Var('L')), Num(-1)), Add(Add(Num(1), Var('x')), Var('i')))), Sub(Add(Div(Mul(Num(-1), Var('K')), Sub(Var('S'), Var('k'))), Num(0)), Var('X'))), Sub(Div(Num(-1), Sub(Sub(Var('A'), Sub(Num(0), Num(-1))), Div(Sub(Var('L'), Var('b')), Sub(Var('j'), Var('z'))))), Sub(Add(Sub(Num(-1), Div(Var('Y'), Var('M'))), Sub(Div(Var('Z'), Num(-1)), Div(Var('a'), Var('P')))), Mul(Div(Add(Num(0), Var('M')), Div(Num(-1), Var('V'))), Num(-1))))), Sub(Mul(Add(Div(Num(0), Mul(Div(Var('M'), Var('K')), Div(Var('u'), Var('q')))), Mul(Add(Add(Var('r'), Num(-1)), Add(Num(0), Var('J'))), Sub(Num(-1), Mul(Num(-1), Var('S'))))), Add(Add(Add(Sub(Var('C'), Var('V')), Var('p')), Mul(Mul(Num(1), Var('Y')), Var('M'))), Add(Var('C'), Add(Mul(Var('T'), Var('M')), Add(Var('O'), Var('y')))))), Sub(Var('y'), Sub(Sub(Var('O'), Div(Sub(Var('f'), Var('j')), Add(Var('P'), Num(-1)))), Sub(Add(Div(Var('W'), Var('T')), Div(Var('b'), Num(-1))), Num(0)))))), Num(-1)), Mul(Mul(Sub(Num(0), Mul(Add(Div(Div(Div(Var('O'), Num(1)), Var('h')), Var('U')), Sub(Add(Sub(Num(1), Var('R')), Var('G')), Num(-1))), Div(Add(Mul(Div(Var('J'), Var('q')), Div(Var('G'), Var('p'))), Mul(Div(Num(1), Var('D')), Var('d'))), Mul(Div(Div(Num(1), Var('I')), Sub(Num(1), Var('C'))), Var('d'))))), Mul(Div(Var('e'), Var('V')), Add(Mul(Mul(Mul(Sub(Var('G'), Var('q')), Num(-1)), Div(Var('M'), Add(Num(0), Num(1)))), Div(Mul(Sub(Num(0), Var('Z')), Add(Var('b'), Var('X'))), Div(Div(Var('K'), Num(1)), Div(Var('F'), Var('d'))))), Div(Add(Sub(Num(0), Div(Num(0), Var('f'))), Sub(Var('l'), Div(Num(1), Var('D')))), Add(Mul(Mul(Num(1), Var('s')), Sub(Var('Y'), Var('u'))), Mul(Div(Num(0), Num(-1)), Mul(Var('d'), Var('k')))))))), Sub(Var('Z'), Var('O')))))))))).simplify()
    #result=Sub(Num(1), Mul(Mul(Num(-1), Div(Div(Sub(Sub(Sub(Sub(Sub(Mul(Div(Add(Add(Sub(Num(1), Var('j')), Var('o')), Var('c')), Add(Add(Div(Var('l'), Var('u')), Add(Num(0), Var('X'))), Div(Sub(Var('g'), Num(1)), Sub(Var('B'), Var('T'))))), Add(Sub(Add(Mul(Var('b'), Num(1)), Sub(Num(0), Num(0))), Num(0)), Var('a'))), Add(Mul(Num(-1), Sub(Mul(Num(-1), Div(Var('s'), Var('L'))), Sub(Sub(Var('b'), Num(-1)), Div(Var('P'), Var('X'))))), Mul(Add(Var('I'), Var('N')), Var('G')))), Add(Sub(Var('s'), Mul(Add(Add(Mul(Num(0), Num(-1)), Add(Var('u'), Var('H'))), Mul(Sub(Num(1), Var('l')), Div(Num(-1), Var('B')))), Var('A'))), Mul(Div(Add(Sub(Var('T'), Num(1)), Num(-1)), Num(-1)), Mul(Div(Var('O'), Add(Add(Var('b'), Var('Q')), Sub(Var('j'), Num(0)))), Sub(Var('L'), Mul(Num(0), Num(1))))))), Var('q')), Sub(Div(Num(1), Add(Var('e'), Sub(Add(Var('Y'), Sub(Add(Div(Num(0), Num(1)), Div(Var('e'), Num(1))), Sub(Sub(Var('Z'), Var('v')), Add(Var('P'), Var('M'))))), Add(Add(Add(Div(Num(0), Var('i')), Num(1)), Sub(Var('U'), Mul(Num(1), Num(-1)))), Mul(Add(Div(Num(1), Var('m')), Mul(Var('e'), Var('M'))), Var('U')))))), Var('c'))), Num(-1)), Add(Div(Var('v'), Div(Add(Num(0), Var('D')), Num(-1))), Mul(Sub(Add(Sub(Var('M'), Sub(Div(Var('f'), Mul(Sub(Var('w'), Num(0)), Var('P'))), Div(Mul(Num(1), Div(Var('p'), Var('T'))), Add(Add(Sub(Num(-1), Var('B')), Var('u')), Div(Sub(Var('i'), Var('r')), Sub(Var('e'), Num(-1))))))), Sub(Sub(Mul(Add(Mul(Div(Var('y'), Var('E')), Num(0)), Sub(Add(Num(1), Num(1)), Sub(Var('G'), Num(0)))), Num(1)), Mul(Var('Z'), Sub(Mul(Mul(Var('u'), Num(-1)), Add(Num(1), Num(1))), Mul(Mul(Var('z'), Var('N')), Num(1))))), Div(Num(0), Num(-1)))), Add(Div(Num(0), Num(-1)), Div(Mul(Add(Mul(Sub(Mul(Num(1), Num(-1)), Mul(Var('O'), Num(0))), Sub(Var('q'), Var('I'))), Add(Sub(Sub(Var('l'), Var('V')), Sub(Var('F'), Var('g'))), Add(Num(1), Div(Var('k'), Num(1))))), Var('e')), Div(Mul(Mul(Div(Div(Var('w'), Num(1)), Var('V')), Sub(Div(Num(0), Var('N')), Sub(Var('s'), Num(0)))), Add(Add(Mul(Num(0), Num(1)), Var('Y')), Sub(Num(-1), Add(Var('G'), Var('R'))))), Sub(Var('t'), Add(Add(Num(-1), Add(Num(1), Var('c'))), Mul(Div(Var('E'), Var('i')), Num(-1)))))))), Var('L')))), Num(-1))), Sub(Div(Mul(Add(Mul(Add(Mul(Div(Sub(Div(Div(Var('a'), Div(Add(Var('K'), Num(0)), Mul(Var('i'), Num(-1)))), Add(Add(Var('m'), Mul(Num(1), Var('A'))), Mul(Num(0), Sub(Var('P'), Num(1))))), Mul(Var('L'), Div(Mul(Div(Num(1), Var('Y')), Div(Var('O'), Var('x'))), Div(Mul(Var('U'), Num(-1)), Sub(Var('Z'), Num(1)))))), Sub(Var('H'), Mul(Mul(Div(Sub(Var('F'), Var('U')), Num(1)), Add(Var('I'), Div(Num(-1), Var('S')))), Mul(Num(1), Div(Var('g'), Num(-1)))))), Mul(Mul(Sub(Var('p'), Sub(Num(1), Var('G'))), Num(0)), Num(0))), Mul(Div(Div(Sub(Add(Add(Sub(Var('I'), Num(1)), Div(Num(1), Var('Q'))), Sub(Div(Var('G'), Num(1)), Num(-1))), Var('J')), Var('c')), Mul(Num(-1), Div(Sub(Num(-1), Mul(Num(1), Mul(Num(0), Num(0)))), Div(Sub(Mul(Num(1), Var('E')), Div(Var('E'), Var('l'))), Add(Div(Var('h'), Num(-1)), Add(Var('V'), Num(-1))))))), Var('E'))), Add(Mul(Mul(Var('C'), Div(Sub(Div(Var('R'), Var('t')), Div(Add(Div(Var('n'), Num(1)), Div(Num(1), Num(-1))), Num(-1))), Mul(Num(-1), Num(-1)))), Num(0)), Mul(Div(Add(Mul(Mul(Mul(Sub(Var('X'), Num(-1)), Mul(Num(1), Var('v'))), Num(0)), Var('P')), Var('k')), Mul(Div(Add(Var('d'), Var('A')), Add(Mul(Mul(Num(-1), Var('r')), Div(Num(1), Var('D'))), Num(-1))), Sub(Add(Div(Var('A'), Var('Z')), Add(Add(Var('L'), Num(0)), Div(Var('T'), Num(1)))), Div(Div(Add(Num(1), Var('b')), Div(Num(-1), Num(1))), Div(Mul(Var('I'), Var('n')), Add(Var('B'), Var('E'))))))), Div(Add(Mul(Add(Add(Add(Num(1), Num(0)), Sub(Num(1), Num(0))), Mul(Div(Num(-1), Var('S')), Sub(Var('E'), Var('d')))), Add(Mul(Var('F'), Add(Var('n'), Var('n'))), Sub(Num(-1), Div(Var('I'), Num(1))))), Div(Add(Num(1), Var('e')), Num(1))), Var('Y'))))), Var('x')), Sub(Sub(Mul(Sub(Add(Div(Num(0), Var('D')), Add(Mul(Num(0), Mul(Sub(Num(1), Sub(Var('L'), Var('C'))), Div(Mul(Num(1), Num(0)), Add(Num(0), Num(-1))))), Sub(Mul(Div(Mul(Var('H'), Num(1)), Div(Var('O'), Num(-1))), Mul(Var('t'), Num(0))), Mul(Sub(Mul(Var('j'), Num(0)), Var('E')), Add(Var('J'), Num(1)))))), Var('P')), Sub(Sub(Div(Sub(Mul(Sub(Sub(Var('P'), Var('t')), Var('V')), Num(-1)), Div(Sub(Sub(Var('o'), Num(0)), Div(Num(1), Var('m'))), Num(1))), Sub(Sub(Mul(Add(Num(0), Num(-1)), Div(Var('f'), Var('e'))), Div(Mul(Var('f'), Num(-1)), Div(Var('X'), Var('J')))), Mul(Mul(Mul(Var('G'), Var('n')), Sub(Var('O'), Var('y'))), Num(1)))), Div(Num(-1), Mul(Num(1), Num(1)))), Add(Add(Mul(Sub(Div(Add(Num(-1), Num(1)), Var('D')), Mul(Add(Var('q'), Var('f')), Mul(Num(0), Var('D')))), Add(Div(Add(Num(1), Var('m')), Num(-1)), Var('i'))), Var('Z')), Div(Mul(Mul(Num(1), Num(0)), Div(Div(Mul(Num(-1), Var('N')), Add(Num(-1), Num(-1))), Sub(Mul(Var('k'), Num(0)), Div(Var('x'), Var('L'))))), Num(1))))), Sub(Num(1), Div(Add(Num(-1), Var('F')), Sub(Sub(Mul(Var('g'), Num(0)), Num(-1)), Sub(Mul(Num(1), Mul(Mul(Div(Var('O'), Num(-1)), Sub(Var('e'), Var('N'))), Sub(Mul(Num(1), Var('B')), Sub(Num(0), Var('r'))))), Mul(Div(Add(Num(1), Num(1)), Div(Sub(Var('b'), Num(0)), Add(Num(-1), Var('K')))), Add(Var('A'), Num(-1)))))))), Div(Mul(Num(1), Add(Div(Sub(Sub(Add(Sub(Mul(Num(-1), Var('N')), Mul(Var('a'), Num(0))), Mul(Sub(Var('d'), Num(1)), Num(0))), Mul(Div(Mul(Num(-1), Num(-1)), Div(Var('B'), Var('u'))), Div(Div(Var('i'), Var('W')), Sub(Num(0), Num(1))))), Mul(Var('h'), Var('b'))), Mul(Var('X'), Var('t'))), Var('h'))), Mul(Var('g'), Add(Add(Div(Mul(Add(Sub(Num(-1), Mul(Var('f'), Var('D'))), Mul(Div(Var('W'), Var('M')), Num(0))), Num(0)), Var('m')), Sub(Var('g'), Var('j'))), Div(Div(Var('d'), Sub(Div(Div(Num(1), Sub(Num(0), Var('J'))), Var('s')), Div(Mul(Mul(Num(1), Num(1)), Add(Num(-1), Var('Q'))), Add(Div(Num(1), Var('b')), Add(Var('P'), Var('Q')))))), Div(Div(Sub(Add(Num(-1), Add(Var('x'), Var('x'))), Var('J')), Mul(Var('X'), Num(1))), Var('b')))))))), Mul(Mul(Add(Num(1), Div(Div(Add(Add(Add(Div(Sub(Num(1), Add(Num(0), Var('t'))), Add(Div(Num(0), Var('s')), Mul(Var('p'), Var('V')))), Mul(Add(Sub(Var('q'), Num(0)), Div(Var('D'), Var('M'))), Div(Div(Num(-1), Num(1)), Div(Num(-1), Var('Z'))))), Sub(Add(Num(1), Mul(Add(Var('n'), Var('z')), Add(Num(0), Num(1)))), Sub(Div(Add(Num(1), Var('e')), Var('A')), Var('M')))), Mul(Add(Sub(Add(Mul(Var('Q'), Var('V')), Div(Var('W'), Var('u'))), Mul(Div(Var('q'), Var('q')), Sub(Var('y'), Var('y')))), Sub(Num(0), Num(-1))), Add(Mul(Mul(Add(Num(-1), Var('m')), Sub(Var('Z'), Num(1))), Mul(Sub(Num(0), Num(0)), Div(Var('V'), Var('n')))), Div(Add(Sub(Var('w'), Num(-1)), Var('f')), Sub(Add(Num(0), Num(-1)), Div(Var('Y'), Var('A'))))))), Sub(Div(Div(Mul(Var('S'), Sub(Sub(Num(-1), Num(0)), Sub(Var('T'), Num(1)))), Mul(Sub(Div(Var('W'), Var('j')), Add(Var('a'), Num(-1))), Var('V'))), Div(Mul(Mul(Div(Num(1), Var('L')), Sub(Num(0), Num(1))), Var('o')), Mul(Mul(Mul(Var('p'), Var('L')), Sub(Num(-1), Var('P'))), Div(Sub(Num(-1), Num(0)), Num(1))))), Mul(Sub(Div(Mul(Num(-1), Mul(Var('i'), Var('m'))), Sub(Add(Num(-1), Var('I')), Div(Var('x'), Var('h')))), Sub(Div(Num(1), Add(Var('k'), Num(-1))), Mul(Mul(Var('P'), Var('F')), Mul(Var('K'), Var('h'))))), Sub(Add(Div(Add(Var('b'), Var('T')), Mul(Num(-1), Num(-1))), Mul(Add(Num(1), Num(1)), Num(-1))), Mul(Add(Sub(Num(0), Num(1)), Div(Var('a'), Var('u'))), Mul(Div(Num(-1), Num(1)), Add(Var('y'), Var('Q')))))))), Sub(Num(0), Num(1)))), Mul(Div(Div(Var('W'), Sub(Div(Var('H'), Num(1)), Div(Div(Num(1), Div(Add(Mul(Var('j'), Var('M')), Var('D')), Var('A'))), Sub(Div(Var('S'), Var('P')), Var('O'))))), Var('z')), Add(Add(Div(Div(Add(Add(Sub(Mul(Num(-1), Var('i')), Div(Num(1), Var('C'))), Num(1)), Var('v')), Sub(Mul(Add(Mul(Num(-1), Num(1)), Add(Var('v'), Num(-1))), Div(Add(Num(1), Num(1)), Div(Num(1), Var('n')))), Add(Num(1), Sub(Var('V'), Num(0))))), Mul(Div(Div(Mul(Num(1), Sub(Num(0), Num(1))), Div(Sub(Var('M'), Var('M')), Sub(Var('B'), Var('x')))), Add(Mul(Var('z'), Mul(Var('v'), Var('b'))), Div(Num(0), Add(Var('r'), Var('p'))))), Sub(Mul(Div(Mul(Num(-1), Var('B')), Sub(Var('R'), Num(1))), Mul(Sub(Num(0), Num(1)), Sub(Num(-1), Num(-1)))), Var('c')))), Mul(Num(0), Mul(Add(Sub(Div(Mul(Num(1), Num(1)), Div(Num(-1), Num(1))), Mul(Add(Num(0), Var('r')), Sub(Num(-1), Var('Q')))), Var('w')), Mul(Var('C'), Var('V'))))), Div(Var('m'), Sub(Sub(Add(Sub(Var('D'), Sub(Var('T'), Add(Num(1), Var('e')))), Var('l')), Mul(Num(0), Sub(Mul(Num(1), Mul(Var('A'), Var('F'))), Sub(Num(0), Mul(Var('n'), Num(0)))))), Add(Mul(Div(Sub(Sub(Var('r'), Num(0)), Var('f')), Mul(Num(-1), Add(Var('Y'), Var('q')))), Mul(Div(Add(Var('B'), Var('H')), Div(Num(-1), Var('c'))), Var('I'))), Num(1))))))), Sub(Div(Add(Num(1), Div(Mul(Div(Var('h'), Mul(Add(Add(Add(Var('E'), Num(0)), Var('u')), Var('L')), Var('p'))), Div(Mul(Var('J'), Add(Sub(Add(Var('j'), Num(-1)), Div(Num(1), Var('Y'))), Mul(Mul(Var('Y'), Num(-1)), Var('d')))), Div(Mul(Add(Num(0), Add(Num(-1), Var('l'))), Sub(Div(Num(0), Num(1)), Num(-1))), Add(Add(Div(Num(-1), Num(-1)), Div(Var('D'), Num(-1))), Sub(Add(Num(1), Var('W')), Div(Var('Z'), Num(1))))))), Var('y'))), Div(Div(Add(Add(Var('d'), Mul(Div(Add(Sub(Var('m'), Num(0)), Div(Num(0), Num(-1))), Div(Sub(Var('g'), Var('i')), Div(Num(1), Num(-1)))), Div(Mul(Div(Var('o'), Var('k')), Sub(Num(1), Var('k'))), Div(Add(Num(-1), Var('a')), Sub(Num(1), Var('B')))))), Add(Var('i'), Div(Sub(Div(Add(Num(1), Num(-1)), Sub(Var('u'), Var('N'))), Div(Div(Var('J'), Var('n')), Var('J'))), Sub(Div(Mul(Num(1), Var('N')), Sub(Num(0), Var('B'))), Mul(Add(Num(-1), Num(-1)), Div(Num(-1), Num(-1))))))), Mul(Num(-1), Num(-1))), Sub(Add(Mul(Add(Sub(Sub(Num(-1), Sub(Var('S'), Num(1))), Mul(Add(Num(0), Var('y')), Num(1))), Div(Div(Add(Var('n'), Var('M')), Sub(Num(-1), Num(0))), Var('H'))), Div(Sub(Sub(Sub(Var('B'), Var('R')), Var('l')), Var('I')), Var('P'))), Add(Num(1), Mul(Var('k'), Mul(Mul(Mul(Num(0), Num(1)), Mul(Var('s'), Num(0))), Num(0))))), Mul(Div(Num(1), Num(1)), Num(0))))), Add(Mul(Mul(Add(Mul(Mul(Div(Div(Sub(Var('l'), Var('b')), Add(Var('E'), Num(0))), Sub(Mul(Var('n'), Num(0)), Var('K'))), Sub(Mul(Mul(Var('n'), Var('I')), Add(Var('n'), Num(0))), Num(-1))), Mul(Num(1), Num(0))), Add(Div(Num(0), Sub(Mul(Sub(Num(0), Num(-1)), Mul(Var('I'), Num(0))), Add(Div(Var('m'), Num(1)), Div(Var('x'), Var('s'))))), Mul(Mul(Sub(Add(Num(1), Num(-1)), Var('R')), Num(0)), Div(Add(Sub(Num(1), Num(0)), Add(Var('L'), Num(0))), Sub(Num(1), Sub(Num(-1), Var('G'))))))), Mul(Div(Sub(Div(Sub(Div(Num(-1), Var('D')), Sub(Num(-1), Var('i'))), Num(-1)), Mul(Add(Sub(Var('l'), Var('t')), Sub(Num(-1), Var('i'))), Mul(Sub(Var('n'), Var('w')), Add(Var('f'), Num(1))))), Div(Var('V'), Sub(Var('c'), Num(-1)))), Num(1))), Num(1)), Add(Sub(Var('I'), Add(Add(Sub(Div(Div(Num(-1), Var('A')), Var('n')), Div(Mul(Mul(Var('X'), Var('i')), Div(Var('J'), Var('H'))), Sub(Add(Num(0), Var('r')), Sub(Num(-1), Num(-1))))), Num(1)), Add(Var('w'), Mul(Var('C'), Add(Sub(Num(-1), Add(Var('I'), Num(-1))), Add(Var('B'), Mul(Num(-1), Var('k')))))))), Mul(Var('Z'), Sub(Div(Mul(Num(-1), Sub(Var('u'), Div(Mul(Var('y'), Var('l')), Var('O')))), Sub(Mul(Add(Mul(Var('Y'), Num(-1)), Add(Num(1), Num(0))), Sub(Add(Num(-1), Num(1)), Var('a'))), Add(Var('n'), Add(Div(Var('y'), Num(1)), Div(Var('E'), Num(-1)))))), Div(Mul(Sub(Add(Mul(Var('B'), Var('r')), Sub(Var('P'), Num(0))), Num(-1)), Sub(Num(1), Div(Sub(Var('G'), Num(0)), Num(-1)))), Div(Sub(Add(Add(Num(-1), Num(1)), Add(Num(1), Num(-1))), Num(-1)), Var('j')))))))))), Mul(Add(Div(Sub(Add(Var('U'), Sub(Sub(Mul(Add(Mul(Div(Sub(Num(0), Num(1)), Num(-1)), Div(Mul(Num(1), Num(1)), Div(Var('l'), Num(-1)))), Add(Var('W'), Num(-1))), Sub(Mul(Div(Mul(Var('y'), Var('e')), Div(Var('C'), Var('L'))), Div(Add(Num(1), Var('p')), Mul(Var('G'), Num(-1)))), Sub(Var('X'), Div(Sub(Var('E'), Var('r')), Add(Var('F'), Var('X')))))), Add(Div(Mul(Var('L'), Add(Div(Var('V'), Num(-1)), Num(1))), Div(Mul(Add(Var('R'), Num(0)), Sub(Var('w'), Var('T'))), Mul(Sub(Var('b'), Var('q')), Div(Var('G'), Num(-1))))), Mul(Sub(Div(Div(Num(1), Num(-1)), Num(1)), Sub(Div(Var('d'), Var('y')), Sub(Num(1), Var('d')))), Sub(Var('q'), Num(1))))), Num(-1))), Sub(Num(0), Div(Num(-1), Mul(Sub(Add(Sub(Div(Div(Num(-1), Num(1)), Sub(Var('U'), Var('g'))), Var('B')), Div(Div(Div(Num(0), Var('e')), Sub(Var('B'), Num(0))), Add(Num(-1), Num(-1)))), Mul(Num(0), Var('N'))), Sub(Mul(Var('o'), Num(0)), Num(1)))))), Mul(Add(Mul(Add(Div(Mul(Add(Add(Sub(Var('r'), Var('E')), Num(0)), Div(Div(Var('N'), Num(-1)), Div(Var('X'), Var('S')))), Add(Add(Num(-1), Div(Num(-1), Var('W'))), Sub(Var('Z'), Var('P')))), Div(Sub(Sub(Mul(Var('Q'), Num(1)), Add(Num(0), Num(-1))), Mul(Mul(Num(1), Var('l')), Add(Var('n'), Var('t')))), Add(Mul(Sub(Var('X'), Num(-1)), Div(Num(-1), Var('p'))), Num(1)))), Add(Add(Var('M'), Sub(Sub(Add(Num(0), Num(-1)), Mul(Var('V'), Var('N'))), Num(1))), Sub(Sub(Var('D'), Mul(Div(Var('R'), Var('B')), Num(0))), Sub(Sub(Var('T'), Var('Y')), Add(Mul(Var('a'), Num(-1)), Var('V')))))), Add(Var('I'), Add(Sub(Mul(Add(Mul(Var('V'), Num(-1)), Div(Num(-1), Num(-1))), Div(Div(Var('M'), Var('E')), Var('D'))), Num(1)), Sub(Div(Num(-1), Num(1)), Div(Add(Div(Num(1), Var('o')), Div(Num(1), Var('n'))), Div(Num(1), Mul(Var('W'), Num(-1)))))))), Num(-1)), Num(-1))), Add(Div(Num(0), Div(Sub(Div(Mul(Mul(Sub(Mul(Sub(Num(0), Var('L')), Var('Q')), Sub(Div(Num(1), Num(1)), Div(Var('E'), Num(1)))), Add(Div(Add(Var('V'), Var('g')), Div(Var('o'), Num(1))), Add(Div(Var('q'), Num(-1)), Sub(Var('N'), Num(-1))))), Sub(Add(Sub(Sub(Num(0), Num(1)), Sub(Var('X'), Var('o'))), Div(Mul(Var('Y'), Var('e')), Add(Num(0), Var('q')))), Sub(Div(Var('W'), Div(Var('I'), Num(-1))), Add(Mul(Var('Z'), Num(-1)), Add(Num(1), Var('v')))))), Sub(Sub(Num(-1), Sub(Num(0), Num(-1))), Mul(Num(0), Div(Mul(Div(Var('f'), Var('D')), Sub(Num(0), Var('Z'))), Sub(Add(Num(1), Num(1)), Sub(Var('x'), Var('k'))))))), Add(Sub(Add(Add(Mul(Div(Var('V'), Var('u')), Sub(Num(1), Var('n'))), Add(Sub(Var('Y'), Var('o')), Add(Num(-1), Num(0)))), Mul(Div(Num(1), Div(Var('Q'), Num(1))), Div(Var('s'), Div(Var('z'), Var('P'))))), Add(Var('N'), Var('i'))), Sub(Sub(Div(Sub(Div(Num(0), Var('k')), Var('K')), Var('q')), Sub(Div(Var('X'), Add(Num(0), Var('z'))), Num(-1))), Var('B')))), Mul(Num(1), Div(Sub(Sub(Div(Num(1), Sub(Div(Num(-1), Num(-1)), Sub(Num(-1), Num(-1)))), Div(Sub(Sub(Var('j'), Num(-1)), Div(Var('m'), Var('w'))), Div(Add(Num(0), Var('Q')), Add(Var('e'), Num(1))))), Sub(Sub(Add(Sub(Var('a'), Var('z')), Div(Num(-1), Num(-1))), Sub(Num(-1), Div(Var('N'), Num(-1)))), Mul(Sub(Add(Var('n'), Num(0)), Mul(Num(1), Num(1))), Mul(Num(0), Div(Num(-1), Var('B')))))), Add(Mul(Var('V'), Add(Sub(Add(Var('T'), Num(0)), Div(Var('p'), Var('F'))), Var('Y'))), Add(Div(Mul(Num(1), Sub(Num(0), Num(-1))), Var('z')), Mul(Div(Div(Num(0), Var('y')), Add(Num(-1), Num(0))), Div(Add(Num(0), Var('h')), Add(Var('v'), Num(-1)))))))))), Num(0))), Mul(Add(Sub(Div(Sub(Var('M'), Mul(Var('x'), Div(Var('l'), Add(Mul(Div(Add(Num(1), Var('T')), Sub(Var('N'), Var('q'))), Sub(Div(Num(-1), Var('T')), Add(Num(0), Var('T')))), Div(Sub(Add(Num(0), Var('L')), Sub(Num(0), Var('q'))), Mul(Div(Var('w'), Num(1)), Add(Var('f'), Num(-1)))))))), Sub(Sub(Div(Sub(Num(0), Mul(Sub(Add(Var('k'), Num(1)), Div(Var('N'), Num(-1))), Add(Mul(Num(1), Num(1)), Mul(Num(-1), Var('I'))))), Mul(Num(1), Add(Div(Sub(Var('t'), Var('h')), Mul(Var('i'), Var('Y'))), Mul(Mul(Var('W'), Num(1)), Num(1))))), Sub(Var('b'), Num(-1))), Add(Add(Div(Num(-1), Sub(Sub(Var('n'), Add(Num(0), Num(-1))), Sub(Mul(Num(-1), Num(0)), Div(Num(0), Var('V'))))), Add(Mul(Sub(Add(Num(0), Var('U')), Div(Var('D'), Var('d'))), Num(0)), Div(Div(Num(-1), Mul(Var('D'), Num(1))), Num(-1)))), Mul(Sub(Num(-1), Sub(Add(Div(Var('i'), Num(-1)), Mul(Num(0), Var('v'))), Div(Div(Var('F'), Var('m')), Div(Var('x'), Num(-1))))), Add(Var('L'), Sub(Add(Add(Var('B'), Var('W')), Mul(Num(-1), Var('c'))), Num(1))))))), Mul(Add(Add(Add(Sub(Mul(Var('H'), Num(1)), Sub(Sub(Mul(Var('b'), Num(1)), Div(Num(1), Num(1))), Sub(Sub(Var('R'), Var('B')), Mul(Num(1), Num(1))))), Var('T')), Num(-1)), Var('I')), Sub(Add(Div(Add(Mul(Div(Var('U'), Div(Var('t'), Var('l'))), Mul(Mul(Num(0), Var('D')), Sub(Var('i'), Num(0)))), Mul(Add(Var('s'), Add(Var('V'), Var('a'))), Var('K'))), Add(Add(Mul(Var('V'), Var('m')), Div(Div(Num(0), Num(-1)), Div(Num(-1), Var('u')))), Add(Num(-1), Add(Sub(Num(-1), Var('e')), Num(-1))))), Mul(Mul(Add(Var('W'), Sub(Mul(Var('v'), Var('k')), Sub(Var('Y'), Num(0)))), Div(Mul(Var('B'), Sub(Num(0), Num(-1))), Mul(Div(Num(1), Var('y')), Num(-1)))), Sub(Add(Var('z'), Sub(Mul(Var('Q'), Num(0)), Div(Num(0), Num(1)))), Num(0)))), Add(Var('I'), Div(Add(Sub(Var('x'), Num(-1)), Add(Var('Q'), Add(Div(Var('u'), Var('o')), Add(Var('D'), Var('V'))))), Add(Var('e'), Num(1))))))), Mul(Sub(Add(Mul(Mul(Add(Sub(Add(Mul(Var('T'), Var('R')), Div(Num(1), Var('q'))), Sub(Var('O'), Div(Num(-1), Var('F')))), Var('Y')), Num(-1)), Mul(Var('N'), Sub(Var('S'), Num(0)))), Var('x')), Var('A')), Var('O'))), Mul(Add(Sub(Add(Add(Div(Mul(Add(Var('D'), Div(Div(Num(0), Num(-1)), Div(Num(1), Var('m')))), Var('X')), Add(Div(Var('X'), Add(Add(Num(0), Num(0)), Add(Var('V'), Num(-1)))), Sub(Mul(Div(Var('q'), Var('L')), Num(1)), Div(Div(Var('S'), Num(-1)), Mul(Var('e'), Num(-1)))))), Add(Add(Div(Sub(Mul(Num(-1), Num(1)), Var('H')), Mul(Mul(Var('b'), Num(-1)), Sub(Num(-1), Var('j')))), Mul(Sub(Sub(Var('p'), Var('j')), Sub(Num(0), Var('S'))), Sub(Mul(Num(-1), Var('s')), Add(Var('d'), Var('z'))))), Sub(Mul(Num(-1), Sub(Mul(Num(-1), Var('r')), Div(Num(1), Var('V')))), Sub(Div(Div(Var('F'), Num(1)), Div(Var('m'), Num(-1))), Div(Add(Num(-1), Var('Z')), Mul(Var('X'), Num(1))))))), Var('x')), Mul(Div(Div(Add(Mul(Div(Div(Var('K'), Var('v')), Div(Var('M'), Var('s'))), Sub(Sub(Var('a'), Var('A')), Var('A'))), Num(-1)), Add(Div(Sub(Mul(Num(1), Num(1)), Num(-1)), Sub(Sub(Var('m'), Var('T')), Add(Num(1), Num(-1)))), Sub(Sub(Add(Num(-1), Var('K')), Sub(Num(1), Num(-1))), Num(1)))), Num(-1)), Div(Add(Mul(Num(1), Mul(Mul(Num(-1), Mul(Num(0), Var('t'))), Add(Mul(Var('s'), Var('U')), Add(Var('p'), Num(-1))))), Num(1)), Div(Div(Var('a'), Num(-1)), Add(Add(Sub(Div(Var('r'), Var('j')), Sub(Var('R'), Num(-1))), Sub(Var('n'), Add(Var('Q'), Num(0)))), Div(Div(Sub(Var('y'), Var('P')), Sub(Var('i'), Var('Q'))), Sub(Add(Num(0), Var('m')), Div(Var('n'), Var('J'))))))))), Mul(Num(-1), Add(Var('d'), Div(Num(0), Div(Num(-1), Add(Sub(Var('I'), Add(Var('c'), Div(Num(0), Num(-1)))), Div(Div(Div(Var('v'), Var('A')), Sub(Num(0), Num(-1))), Div(Mul(Var('b'), Num(1)), Mul(Var('S'), Num(1)))))))))), Sub(Sub(Sub(Div(Div(Div(Mul(Div(Mul(Num(0), Var('r')), Sub(Var('C'), Var('G'))), Div(Sub(Var('O'), Num(-1)), Add(Num(1), Var('q')))), Add(Div(Mul(Num(-1), Var('L')), Num(-1)), Add(Add(Num(1), Var('x')), Var('i')))), Sub(Add(Div(Mul(Num(-1), Var('K')), Sub(Var('S'), Var('k'))), Num(0)), Var('X'))), Sub(Div(Num(-1), Sub(Sub(Var('A'), Sub(Num(0), Num(-1))), Div(Sub(Var('L'), Var('b')), Sub(Var('j'), Var('z'))))), Sub(Add(Sub(Num(-1), Div(Var('Y'), Var('M'))), Sub(Div(Var('Z'), Num(-1)), Div(Var('a'), Var('P')))), Mul(Div(Add(Num(0), Var('M')), Div(Num(-1), Var('V'))), Num(-1))))), Sub(Mul(Add(Div(Num(0), Mul(Div(Var('M'), Var('K')), Div(Var('u'), Var('q')))), Mul(Add(Add(Var('r'), Num(-1)), Add(Num(0), Var('J'))), Sub(Num(-1), Mul(Num(-1), Var('S'))))), Add(Add(Add(Sub(Var('C'), Var('V')), Var('p')), Mul(Mul(Num(1), Var('Y')), Var('M'))), Add(Var('C'), Add(Mul(Var('T'), Var('M')), Add(Var('O'), Var('y')))))), Sub(Var('y'), Sub(Sub(Var('O'), Div(Sub(Var('f'), Var('j')), Add(Var('P'), Num(-1)))), Sub(Add(Div(Var('W'), Var('T')), Div(Var('b'), Num(-1))), Num(0)))))), Num(-1)), Mul(Mul(Sub(Num(0), Mul(Add(Div(Div(Div(Var('O'), Num(1)), Var('h')), Var('U')), Sub(Add(Sub(Num(1), Var('R')), Var('G')), Num(-1))), Div(Add(Mul(Div(Var('J'), Var('q')), Div(Var('G'), Var('p'))), Mul(Div(Num(1), Var('D')), Var('d'))), Mul(Div(Div(Num(1), Var('I')), Sub(Num(1), Var('C'))), Var('d'))))), Mul(Div(Var('e'), Var('V')), Add(Mul(Mul(Mul(Sub(Var('G'), Var('q')), Num(-1)), Div(Var('M'), Add(Num(0), Num(1)))), Div(Mul(Sub(Num(0), Var('Z')), Add(Var('b'), Var('X'))), Div(Div(Var('K'), Num(1)), Div(Var('F'), Var('d'))))), Div(Add(Sub(Num(0), Div(Num(0), Var('f'))), Sub(Var('l'), Div(Num(1), Var('D')))), Add(Mul(Mul(Num(1), Var('s')), Sub(Var('Y'), Var('u'))), Mul(Div(Num(0), Num(-1)), Mul(Var('d'), Var('k')))))))), Sub(Var('Z'), Var('O')))))))))).simplify()