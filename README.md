# Symbolic Algebra

A Python-based symbolic algebra system built for **MIT 6.101**. This project implements a fully functional expression tree that supports constructing, displaying, evaluating, differentiating, and simplifying mathematical expressions.

## Features

- **Expression Construction** — Build symbolic expressions using Python's native operators (`+`, `-`, `*`, `/`) with automatic type coercion for `int`, `float`, and `str` values.
- **Pretty Printing** — Expressions render with minimal parentheses using operator precedence rules (`repr` and `str` both supported).
- **Evaluation** — Evaluate expressions numerically by providing a variable-to-value mapping.
- **Symbolic Differentiation** — Compute derivatives with respect to any variable using standard calculus rules (sum, product, and quotient rules).
- **Simplification** — Simplify expressions by folding constants and eliminating identity operations (e.g., `x + 0 → x`, `x * 1 → x`).

## Class Hierarchy

```
Expr (base)
├── Num   — numeric literals
├── Var   — named variables
└── BinOp — binary operations
    ├── Add (+)
    ├── Sub (-)
    ├── Mul (*)
    └── Div (/)
```

## Quick Start

```python
from lab import *

# Build an expression: (x + 2) * y
expr = (Var('x') + 2) * Var('y')

# Evaluate with x=3, y=5
print(expr.evaluate({'x': 3, 'y': 5}))  # 25

# Differentiate with respect to x
print(expr.deriv('x'))  # y * 1 + 0 * (x + 2) → simplifies to y

# Simplify
print(expr.deriv('x').simplify())  # y
```

## Running Tests

```bash
pytest test.py
```
