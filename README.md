# 🧠 Symbolic Algebra Engine

This project is a symbolic algebra interpreter built in Python as part of the [6.101 Lab: Symbolic Algebra]. It parses and manipulates algebraic expressions using a custom class hierarchy. Key features include simplification, differentiation, and symbolic evaluation.

---

## ✨ Features

- **Expression Tree Structure**  
  Each algebraic expression is represented as a tree of objects (`Num`, `Var`, `Add`, `Sub`, `Mul`, `Div`), enabling recursive operations.

- **Parsing & Tokenizing**  
  - Converts infix string expressions (e.g., `"x + (3 * y)"`) into object trees.  
  - Handles nested parentheses and negative numbers.

- **Evaluation**  
  Supports substitution-based evaluation using mappings like `{ 'x': 5, 'y': 2 }`.

- **Differentiation**  
  Computes symbolic derivatives with respect to a given variable.

- **Simplification**  
  Automatically reduces expressions (e.g., `x + 0 → x`, `0 * y → 0`, `x / 1 → x`).

---

## 🧪 Example Usage

```python
expr = make_expression("( x + ( 3 * y ) )")
print(expr)               # Output: x + 3 * y

print(expr.evaluate({'x': 2, 'y': 4}))  # Output: 14

print(expr.deriv('x'))    # Output: 1
print(expr.deriv('y'))    # Output: 3

print(expr.simplify())    # Output: x + 3 * y
