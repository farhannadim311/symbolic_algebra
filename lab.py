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


class Expr:
    """
    Represents an Expression in a symbolic algebra system
    """
    pass


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

    def __repr__(self):
        return f"Var('{self.name}')"


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
class Add(BinOp):
    """
    Represents Addition
    """
    pass

class Sub(BinOp):
    """
    Represents Subtraction
    """
    pass

class Mul(BinOp):
    """
    Represents Multiplication
    """
    pass

class Div(BinOp):
    """
    Represents Division
    """
    pass


if __name__ == "__main__":
    z = Add(Var('x'), Sub(Var('y'), Num(2)))
    print(repr(z))

