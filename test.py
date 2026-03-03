"""
6.101 Lab:
Symbolic Algebra
"""

#!/usr/bin/env python3
import os
import lab
import ast
import pytest
import random
import builtins

ttype = type
iisinstance = isinstance


def with_no_type_checks(test, mix_up_symbols=False, do_symbols=True, do_names=True):
    def type_checking_test(*args, **kwargs):
        if mix_up_symbols:
            with_mixed_up_symbols(test, do_symbols, do_names)(*args, **kwargs)
        with_no_explicit_type_checking(test)(*args, **kwargs)

    return type_checking_test


def with_mixed_up_symbols(test, do_symbols=True, do_names=True):
    """
    Runs a test, checking for explicit type-checking.
    If this test fails but the corresponding test fails, there is likely some
    kind of disallowed type-checking happening
    """

    def new_test(*args):
        symbols = {lab.Add: "+", lab.Sub: "-", lab.Mul: "*", lab.Div: "/"}
        oclasses = {c.__name__: c for c in symbols}

        orig = list(oclasses)
        shuf = list(orig)
        while shuf == orig:
            random.shuffle(shuf)

        mixed_classes = {}
        for oldname, newname in zip(orig, shuf):
            oldclass = oclasses[oldname]
            newclass = oclasses[newname]
            oldsymbol = symbols[oldclass]
            newsymbol = symbols[newclass]
            mixed_classes[oldname] = ttype(
                oldname, oldclass.__bases__, dict(oldclass.__dict__)
            )
            for attr in set(oldclass.__dict__) | set(newclass.__dict__):
                if do_symbols:
                    if (
                        getattr(oldclass, attr, None) == oldsymbol
                        or getattr(newclass, attr, None) == newsymbol
                    ):
                        setattr(mixed_classes[oldname], attr, newsymbol)
                if do_names:
                    if (
                        getattr(oldclass, attr, None) == oldname
                        or getattr(newclass, attr, None) == newname
                    ):
                        setattr(mixed_classes[oldname], attr, newname)

        for name, cls in mixed_classes.items():
            setattr(lab, name, cls)

        try:
            test()
        except DisallowedFunctionException:
            raise
        except Exception as e:
            assert (
                False
            ), f"Incorrect error, which may be due to bug or incorrect type checking!"
        finally:
            for name, cls in oclasses.items():
                setattr(lab, name, cls)

    return new_test


def with_no_explicit_type_checking(testcase):
    """
    Runs a test, checking for explicit type-checking.
    If this test fails but the corresponding test fails, there is likely some
    kind of disallowed type-checking happening
    """

    def the_test(*args, **kwargs):
        otype = builtins.type
        oii = builtins.isinstance

        ofuncs = {}
        classobjs = {}

        method_stack = []

        for val in list(lab.__dict__.values()):
            if isinstance(val, type):
                if val is type:
                    continue
                for methodname in ("__init__", "simplify"):
                    if methodname not in val.__dict__:
                        continue
                    classobjs[val.__name__] = val

                    method = getattr(val, methodname, None)
                    ofuncs.setdefault(val.__name__, {})[methodname] = method

                    def make_new_func(name, methodname):
                        def _overridden_method(*args, **kwargs):
                            lab.type = otype
                            lab.isinstance = oii
                            method_stack.append(name)
                            try:
                                out = ofuncs[name][methodname](*args, **kwargs)
                            except:
                                raise
                            finally:
                                method_stack.pop()
                                if not method_stack:
                                    lab.type = _disallowed(otype)
                                    lab.isinstance = _disallowed(oii)
                            return out

                        return _overridden_method

                    setattr(val, methodname, make_new_func(val.__name__, methodname))
        lab.type = _disallowed(otype)
        lab.isinstance = _disallowed(oii)
        lab.eval = _disallowed(eval)

        try:
            testcase(*args, **kwargs)
            assert (
                oii not in lab.__dict__.values()
            ), f"You should not re-import isinstance in lab.py!"
            assert (
                otype not in lab.__dict__.values()
            ), f"You should not re-import type in lab.py!"
            assert builtins not in lab.__dict__.values(), f"No importing builtins!"
        except:
            raise
        finally:
            lab.type = otype
            lab.isinstance = oii
            for classname, cls in classobjs.items():
                for omethodname, omethod in ofuncs[cls.__name__].items():
                    setattr(cls, omethodname, omethod)

    return the_test


TEST_DIRECTORY = os.path.dirname(__file__)


def expression_rep(x):
    """
    Recursively converts an Expr object x into a new object consisting of
    only built-in types that can be checked for equality against expected
    results without relying on any lab.py functionality
    """
    if iisinstance(x, lab.BinOp):
        if x.__class__.__name__ in {"Add", "Mul"}:  # commutative operations
            op_rep = frozenset
        elif x.__class__.__name__ in {"Sub", "Div"}:
            op_rep = tuple
        else:
            raise NotImplementedError(f"No support for {ttype(x)}")
        return (
            x.__class__.__name__,
            op_rep(expression_rep(i) for i in (x.left, x.right)),
        )
    elif iisinstance(x, lab.Num):
        return ("Num", x.n)
    elif iisinstance(x, lab.Var):
        return ("Var", x.name)
    else:
        raise NotImplementedError(f"No support for {ttype(x)}")


def expression_hash(x):
    return hash(expression_rep(x))


class DisallowedFunctionException(Exception):
    pass


def _disallowed(f):
    def _disallowed_inner(*args, **kwargs):
        raise DisallowedFunctionException(f"using disallowed function: {f.__name__}")

    return _disallowed_inner

def _display_check(expression, expected, test):
    if test == 0:
        result = repr(expression)
        expected = expected[0]
        try:
            passed = expression_rep(safe_eval(result)) == expression_rep(safe_eval(expected))
        except ValueError:
            passed = False
        assert passed is True, f"Incorrect repr result!\nresult = repr({expected})\n# Got   {result=}\n# But {expected=}"
    else:
        result = str(expression)
        repr_expression, expected = expected
        passed = result == expected
        assert passed is True, f"Incorrect str result!\nresult = str({repr_expression})\n# Got   {result=}\n# But {expected=}"

def _make_test_display_00(test=0):
    def the_test(*args):
        expression = lab.Add(lab.Num(0), lab.Var("x"))
        expected = ("Add(Num(0), Var('x'))", "0 + x")
        _display_check(expression, expected, test)

        expression = lab.Add(lab.Var("x"), lab.Num(0))
        expected = ("Add(Var('x'), Num(0))", "x + 0")
        _display_check(expression, expected, test)

        expression = lab.Mul(lab.Num(1), lab.Var("x"))
        expected = ("Mul(Num(1), Var('x'))", "1 * x")
        _display_check(expression, expected, test)

        expression = lab.Mul(lab.Var("x"), lab.Num(1))
        expected = ("Mul(Var('x'), Num(1))", "x * 1")
        _display_check(expression, expected, test)

        expression = lab.Sub(lab.Var("x"), lab.Num(0))
        expected = ("Sub(Var('x'), Num(0))", "x - 0")
        _display_check(expression, expected, test)

        expression = lab.Div(lab.Var("x"), lab.Num(1))
        expected = ("Div(Var('x'), Num(1))", "x / 1")
        _display_check(expression, expected, test)

        expression = lab.Div(lab.Num(0), lab.Var("x"))
        expected = ("Div(Num(0), Var('x'))", "0 / x")
        _display_check(expression, expected, test)

        expression = lab.Add(lab.Num(20), lab.Num(30))
        expected = ("Add(Num(20), Num(30))", "20 + 30")
        _display_check(expression, expected, test)

        expression = lab.Sub(lab.Num(50), lab.Num(80))
        expected = ("Sub(Num(50), Num(80))", "50 - 80")
        _display_check(expression, expected, test)

        expression = lab.Div(lab.Num(40), lab.Num(20))
        expected = ("Div(Num(40), Num(20))", "40 / 20")
        _display_check(expression, expected, test)

        expression = lab.Mul(lab.Num(101), lab.Num(121))
        expected = ("Mul(Num(101), Num(121))", "101 * 121")
        _display_check(expression, expected, test)

    return the_test


def _make_test_display_01(test=0):
    def the_test(*args):
        expression = lab.Add(lab.Num(0), lab.Mul(lab.Var("y"), lab.Num(2)))
        expected = ("Add(Num(0), Mul(Var('y'), Num(2)))", "0 + y * 2")
        _display_check(expression, expected, test)

        expression = lab.Add(lab.Mul(lab.Var("z"), lab.Num(3)), lab.Num(0))
        expected = ("Add(Mul(Var('z'), Num(3)), Num(0))", "z * 3 + 0")
        _display_check(expression, expected, test)

        expression = lab.Mul(lab.Num(1), lab.Add(lab.Var("A"), lab.Var("x")))
        expected = ("Mul(Num(1), Add(Var('A'), Var('x')))", "1 * (A + x)")
        _display_check(expression, expected, test)

        expression = lab.Mul(lab.Sub(lab.Var("x"), lab.Var("A")), lab.Num(1))
        expected = ("Mul(Sub(Var('x'), Var('A')), Num(1))", "(x - A) * 1")
        _display_check(expression, expected, test)

        expression = lab.Sub(lab.Mul(lab.Var("x"), lab.Num(3)), lab.Num(0))
        expected = ("Sub(Mul(Var('x'), Num(3)), Num(0))", "x * 3 - 0")
        _display_check(expression, expected, test)

        expression = lab.Div(lab.Mul(lab.Num(7), lab.Var("A")), lab.Num(1))
        expected = ("Div(Mul(Num(7), Var('A')), Num(1))", "7 * A / 1")
        _display_check(expression, expected, test)

        expression = lab.Div(lab.Num(0), lab.Add(lab.Var("A"), lab.Num(3)))
        expected = ("Div(Num(0), Add(Var('A'), Num(3)))", "0 / (A + 3)")
        _display_check(expression, expected, test)

        expression = lab.Mul(lab.Add(lab.Num(0), lab.Var("x")), lab.Var("z"))
        expected = ("Mul(Add(Num(0), Var('x')), Var('z'))", "(0 + x) * z")
        _display_check(expression, expected, test)

        expression = lab.Sub(lab.Add(lab.Var("x"), lab.Num(0)), lab.Var("A"))
        expected = ("Sub(Add(Var('x'), Num(0)), Var('A'))", "x + 0 - A")
        _display_check(expression, expected, test)

        expression = lab.Add(lab.Mul(lab.Num(1), lab.Var("x")), lab.Var("y"))
        expected = ("Add(Mul(Num(1), Var('x')), Var('y'))", "1 * x + y")
        _display_check(expression, expected, test)

        expression = lab.Add(lab.Var("z"), lab.Mul(lab.Var("x"), lab.Num(1)))
        expected = ("Add(Var('z'), Mul(Var('x'), Num(1)))", "z + x * 1")
        _display_check(expression, expected, test)

        expression = lab.Sub(lab.Var("A"), lab.Sub(lab.Var("x"), lab.Num(0)))
        expected = ("Sub(Var('A'), Sub(Var('x'), Num(0)))", "A - (x - 0)")
        _display_check(expression, expected, test)

        expression = lab.Div(lab.Var("y"), lab.Div(lab.Var("x"), lab.Num(1)))
        expected = ("Div(Var('y'), Div(Var('x'), Num(1)))", "y / (x / 1)")
        _display_check(expression, expected, test)

        expression = lab.Div(lab.Var("x"), lab.Mul(lab.Num(3), lab.Num(4)))
        expected = ("Div(Var('x'), Mul(Num(3), Num(4)))", "x / (3 * 4)")
        _display_check(expression, expected, test)

        expression = lab.Mul(lab.Var("z"), lab.Div(lab.Num(0), lab.Var("x")))
        expected = ("Mul(Var('z'), Div(Num(0), Var('x')))", "z * 0 / x")
        _display_check(expression, expected, test)

        expression = lab.Add(lab.Mul(lab.Num(0), lab.Var("y")), lab.Var("x"))
        expected = ("Add(Mul(Num(0), Var('y')), Var('x'))", "0 * y + x")
        _display_check(expression, expected, test)

        expression = lab.Add(lab.Var("x"), lab.Sub(lab.Num(2), lab.Num(2)))
        expected = ("Add(Var('x'), Sub(Num(2), Num(2)))", "x + 2 - 2")
        _display_check(expression, expected, test)

        expression = lab.Mul(lab.Div(lab.Num(2), lab.Num(2)), lab.Var("x"))
        expected = ("Mul(Div(Num(2), Num(2)), Var('x'))", "2 / 2 * x")
        _display_check(expression, expected, test)

        expression = lab.Mul(lab.Var("x"), lab.Sub(lab.Num(3), lab.Num(2)))
        expected = ("Mul(Var('x'), Sub(Num(3), Num(2)))", "x * (3 - 2)")
        _display_check(expression, expected, test)

        expression = lab.Sub(lab.Var("x"), lab.Mul(lab.Num(0), lab.Var("z")))
        expected = ("Sub(Var('x'), Mul(Num(0), Var('z')))", "x - 0 * z")
        _display_check(expression, expected, test)

        expression = lab.Div(lab.Var("x"), lab.Num(1))
        expected = ("Div(Var('x'), Num(1))", "x / 1")
        _display_check(expression, expected, test)

        expression = lab.Div(lab.Add(lab.Num(0), lab.Num(0)), lab.Var("x"))
        expected = ("Div(Add(Num(0), Num(0)), Var('x'))", "(0 + 0) / x")
        _display_check(expression, expected, test)

        expression = read_expected("52_in.pyobj")
        expected = read_expected("52_out.pyobj")
        _display_check(expression, expected, test)

        expression = lab.Sub(lab.Add(lab.Num(70), lab.Num(50)), lab.Num(80))
        expected = ("Sub(Add(Num(70), Num(50)), Num(80))", "70 + 50 - 80")
        _display_check(expression, expected, test)

        expression = lab.Sub(lab.Num(80), lab.Div(lab.Num(40), lab.Num(20)))
        expected = ("Sub(Num(80), Div(Num(40), Num(20)))", "80 - 40 / 20")
        _display_check(expression, expected, test)

    return the_test


def _make_test_display_02(test=0):
    def the_test(*args):
        for i in range(55, 64):
            expression = read_expected(f"{i}_in.pyobj")
            expected = read_expected(f"{i}_out.pyobj")
            _display_check(expression, expected, test)

    return the_test

# RUN DISPLAY TESTS


def test_display_repr_behavior():
    _make_test_display_00(0)()
    _make_test_display_01(0)()
    _make_test_display_02(0)()


test_display_str_behavior_00 = _make_test_display_00(1)
test_display_str_behavior_01 = _make_test_display_01(1)
test_display_str_behavior_02 = _make_test_display_02(1)

test_display_repr_behavior_types = with_no_type_checks(
    test_display_repr_behavior, mix_up_symbols=True, do_names=False
)
test_display_str_behavior_00_types = with_no_type_checks(
    test_display_str_behavior_00, mix_up_symbols=True, do_symbols=False
)
test_display_str_behavior_01_types = with_no_type_checks(
    test_display_str_behavior_01, mix_up_symbols=True, do_symbols=False
)
test_display_str_behavior_02_types = with_no_type_checks(
    test_display_str_behavior_02, mix_up_symbols=True, do_symbols=False
)


def _check_combo(result, expected):
    assert isinstance(result, lab.BinOp), f'Unexpected type!'
    assert isinstance(result.left, lab.Expr), f'Unexpected type!'
    assert isinstance(result.right, lab.Expr), f'Unexpected type!'
    assert expression_rep(result) == expected


def test_combinations_00():
    result = 0 + lab.Var("x")
    expected = ("Add", frozenset({("Var", "x"), ("Num", 0)}))
    _check_combo(result, expected)

    result = lab.Var("x") + 0
    expected = ("Add", frozenset({("Var", "x"), ("Num", 0)}))
    _check_combo(result, expected)

    result = 0 + (lab.Var("y") * 2)
    expected = (
        "Add",
        frozenset({("Mul", frozenset({("Num", 2), ("Var", "y")})), ("Num", 0)}),
    )
    _check_combo(result, expected)

    result = ("z" * lab.Num(3)) + 0
    expected = (
        "Add",
        frozenset({("Mul", frozenset({("Num", 3), ("Var", "z")})), ("Num", 0)}),
    )
    _check_combo(result, expected)

    result = (lab.Num(0) + "x") * "z"
    expected = (
        "Mul",
        frozenset({("Var", "z"), ("Add", frozenset({("Var", "x"), ("Num", 0)}))}),
    )
    _check_combo(result, expected)

    result = (0 * lab.Var("y")) + lab.Var("x")
    expected = (
        "Add",
        frozenset({("Mul", frozenset({("Var", "y"), ("Num", 0)})), ("Var", "x")}),
    )
    _check_combo(result, expected)

    result = "x" + (lab.Num(2) - 2)
    expected = ("Add", frozenset({("Var", "x"), ("Sub", (("Num", 2), ("Num", 2)))}))
    _check_combo(result, expected)

    result = 20 + lab.Num(101) * (1 * lab.Var("z"))
    expected = ('Add', frozenset({('Num', 20), ('Mul', frozenset({('Mul', frozenset({('Num', 1), ('Var', 'z')})), ('Num', 101)}))}))
    _check_combo(result, expected)

    result = "x" - lab.Num(101)
    expected = ("Sub", (("Var", "x"), ("Num", 101)))
    _check_combo(result, expected)

    result = "x" / lab.Num(101)
    expected = ("Div", (("Var", "x"), ("Num", 101)))
    _check_combo(result, expected)

    result = lab.Num(101) / "x"
    expected = ("Div", (("Num", 101), ("Var", "x")))
    _check_combo(result, expected)

    result = lab.Num(101) - "x"
    expected = ("Sub", (("Num", 101), ("Var", "x")))
    _check_combo(result, expected)


test_combinations_00_types = with_no_type_checks(
    test_combinations_00, mix_up_symbols=True
)


def _check_eval(inp, vars, expected):
    result = inp.evaluate(vars)
    good_type = isinstance(result, (int, float))
    assert good_type is True, f'Evaluate returned unexpected type!\n{result = }'
    close_enough = abs(result - expected) <= 1e-4
    assert close_enough, f'Evaluate returned incorrect result!\n{repr(inp)}.evaluate({vars})\nGot {result = }\nbut {expected = }'


def test_eval_00():
    inp = lab.Add(lab.Num(0), lab.Var("x"))
    vars = {"x": 877}
    expected = 877
    _check_eval(inp, vars, expected)

    inp = lab.Mul(lab.Num(1), lab.Var("x"))
    vars = {"x": -365}
    expected = -365
    _check_eval(inp, vars, expected)

    inp = lab.Mul(lab.Var("y"), lab.Num(2))
    vars = {"y": -296}
    expected = -592
    _check_eval(inp, vars, expected)

    inp = lab.Add(lab.Mul(lab.Var("z"), lab.Num(3)), lab.Num(0))
    vars = {"z": 400}
    expected = 1200
    _check_eval(inp, vars, expected)

    inp = lab.Div(lab.Mul(lab.Num(7), lab.Var("A")), lab.Num(9))
    vars = {"A": 610}
    expected = 474.44444444444446
    _check_eval(inp, vars, expected)

    inp = lab.Add(lab.Var("z"), lab.Add(lab.Var("x"), lab.Num(1)))
    vars = {"z": -596, "x": -554}
    expected = -1149
    _check_eval(inp, vars, expected)
    with pytest.raises(lab.SymbolicEvaluationError):
        inp.evaluate({"z": 500})

    inp = lab.Sub(lab.Var("A"), lab.Add(lab.Var("x"), lab.Var("A")))
    vars = {"A": 539, "x": -789}
    expected = 789
    _check_eval(inp, vars, expected)
    with pytest.raises(lab.SymbolicEvaluationError):
        inp.evaluate({"A": 5})

    inp = lab.Div(lab.Var("y"), lab.Div(lab.Var("x"), lab.Var("z")))
    vars = {"z": 693, "y": -71, "x": -391}
    expected = 125.83887468030692
    _check_eval(inp, vars, expected)
    with pytest.raises(lab.SymbolicEvaluationError):
        inp.evaluate(
            {
                "z": 693,
                "y": -71,
            }
        )

    inp = lab.Mul(lab.Mul(lab.Var("x"), lab.Var("y")), lab.Var("z"))
    vars = {"z": 816, "y": 732, "x": -225}
    expected = -134395200
    _check_eval(inp, vars, expected)
    with pytest.raises(lab.SymbolicEvaluationError):
        inp.evaluate(
            {
                "z": 693,
                "y": -71,
            }
        )

    inp = read_expected("156_in.pyobj")
    vars = {"z": 984, "A": -801, "x": -880, "y": 96}
    expected = -1815480
    _check_eval(inp, vars, expected)
    with pytest.raises(lab.SymbolicEvaluationError):
        inp.evaluate(
            {
                "z": 693,
                "y": -71,
            }
        )


def test_eval_01():
    inp = lab.Sub(lab.Var("k"), lab.Num(5))
    vars = {"k": 583}
    expected = 578
    _check_eval(inp, vars, expected)
    assert expression_rep(inp) == expression_rep(
        lab.Sub(lab.Var("k"), lab.Num(5))
    ), f"Input to eval should not be mutated!"

    inp = read_expected("158_in.pyobj")
    inp2 = read_expected("158_in.pyobj")
    vars = {
        "Q": -960,
        "T": 696,
        "Y": 895,
        "H": -395,
        "y": -752,
        "F": 973,
        "l": 581,
        "X": 853,
        "G": -370,
        "q": -403,
        "V": 211,
        "v": 203,
        "n": -859,
        "t": -794,
        "o": -710,
        "N": 640,
        "L": 958,
        "g": 46,
        "J": 796,
        "f": 127,
        "w": 706,
        "S": 351,
        "B": 454,
        "O": 45,
        "D": 848,
        "u": -729,
        "E": 394,
        "C": -230,
        "p": -497,
        "a": 494,
        "Z": 890,
        "j": 601,
        "K": -273,
        "I": -432,
        "e": 809,
        "s": 453,
        "i": -90,
        "R": 421,
        "U": 720,
        "P": -248,
        "m": 56,
        "k": -20,
    }
    expected = -24447405.102586962
    _check_eval(inp, vars, expected)
    assert expression_rep(inp) == expression_rep(
        inp2
    ), f"Input to eval should not be mutated!"

    inp = read_expected("159_in.pyobj")
    inp2 = read_expected("159_in.pyobj")
    vars = {
        "P": 865,
        "r": -635,
        "g": -328,
        "L": -77,
        "b": 272,
        "B": -892,
        "h": 569,
        "H": -411,
        "D": 606,
        "y": -891,
        "W": 278,
        "u": 411,
        "p": 769,
        "C": -557,
        "z": -478,
        "j": 547,
        "A": -273,
        "K": -671,
        "I": 156,
        "M": -942,
        "s": -991,
        "V": 33,
        "U": 951,
        "m": 695,
        "t": 337,
        "o": -27,
        "N": -392,
        "k": 865,
    }
    expected = 3.079655919243488e-13
    _check_eval(inp, vars, expected)
    assert expression_rep(inp) == expression_rep(
        inp2
    ), f"Input to eval should not be mutated!"

    inp = read_expected("160_in.pyobj")
    inp2 = read_expected("160_in.pyobj")
    vars = {
        "r": -831,
        "Q": -249,
        "T": -12,
        "H": -582,
        "l": -408,
        "G": -796,
        "V": -412,
        "n": -166,
        "N": -116,
        "g": 30,
        "S": -281,
        "B": 969,
        "x": -690,
        "O": 17,
        "W": -977,
        "u": 844,
        "C": -425,
        "Z": -304,
        "j": -617,
        "A": 757,
        "I": 742,
        "i": -660,
        "U": -916,
        "R": -46,
        "b": -809,
        "y": -861,
        "F": 316,
        "z": 295,
        "q": 201,
        "M": 368,
        "v": 952,
        "t": -597,
        "d": 874,
        "o": 745,
        "L": 812,
        "J": -55,
        "w": 153,
        "h": -249,
        "D": -310,
        "p": 289,
        "s": -535,
        "P": 629,
        "m": 705,
        "k": -130,
    }
    expected = -3036189255.554901
    _check_eval(inp, vars, expected)
    assert expression_rep(inp) == expression_rep(
        inp2
    ), f"Input to eval should not be mutated!"

    inp = read_expected("161_in.pyobj")
    inp2 = read_expected("161_in.pyobj")
    vars = {
        "g": 867,
        "L": 954,
        "w": 686,
        "f": -711,
        "o": -227,
        "h": -634,
        "O": 799,
        "y": 594,
        "D": -115,
        "u": 394,
        "a": 960,
        "X": -987,
        "v": -163,
        "U": -887,
        "t": 527,
        "d": 657,
        "N": 400,
    }
    expected = 4741737.246211018
    _check_eval(inp, vars, expected)
    assert expression_rep(inp) == expression_rep(
        inp2
    ), f"Input to eval should not be mutated!"

    inp = read_expected("162_in.pyobj")
    inp2 = read_expected("162_in.pyobj")
    vars = {
        "J": -150,
        "X": -302,
        "w": 332,
        "s": 927,
        "v": -687,
        "B": -740,
        "E": 671,
        "k": -539,
    }
    expected = 347.0000000000164
    _check_eval(inp, vars, expected)
    assert expression_rep(inp) == expression_rep(
        inp2
    ), f"Input to eval should not be mutated!"

    inp = read_expected("163_in.pyobj")
    inp2 = read_expected("163_in.pyobj")
    vars = {
        "P": -228,
        "Q": -6,
        "g": 896,
        "d": -417,
        "T": -870,
        "b": -138,
        "S": 835,
        "x": -405,
        "h": 719,
        "H": 766,
        "y": -982,
        "D": 766,
        "E": -376,
        "C": 832,
        "l": -559,
        "X": 323,
        "K": -630,
        "q": 548,
        "I": -809,
        "V": -849,
        "M": 122,
        "c": 173,
        "o": -875,
        "m": -395,
    }
    expected = -4004783415.5644646
    _check_eval(inp, vars, expected)
    assert expression_rep(inp) == expression_rep(
        inp2
    ), f"Input to eval should not be mutated!"

    inp = read_expected("164_in.pyobj")
    inp2 = read_expected("164_in.pyobj")
    vars = {
        "L": -750,
        "d": -449,
        "T": -230,
        "f": -843,
        "o": 280,
        "O": -840,
        "h": -729,
        "y": -658,
        "D": -724,
        "W": 502,
        "E": 578,
        "F": -198,
        "Z": -23,
        "e": 360,
        "v": 666,
        "U": 927,
        "m": 230,
        "t": -944,
        "P": 742,
        "N": 446,
    }
    expected = 1475.6592465238434
    _check_eval(inp, vars, expected)
    assert expression_rep(inp) == expression_rep(
        inp2
    ), f"Input to eval should not be mutated!"


test_eval_00_types = with_no_type_checks(test_eval_00, mix_up_symbols=True)
test_eval_01_types = with_no_type_checks(test_eval_01, mix_up_symbols=True)


def _check_deriv(expression, expression_copy, expected):
    deriv_vars = [("x",), ("y"), ("x", "x", "x"), ("y", "x"), ("z")]

    def make_err_message():
        out = repr(expression_copy)
        for name in var_names:
            out += f'.deriv({repr(name)})'
        return out

    for var_names, expect in zip(deriv_vars, expected):
        result = expression
        for name in var_names:
            result = result.deriv(name)
            good_type = isinstance(result, lab.Expr)
            assert good_type is True, f'Deriv returned unexpected type!\n{result = }'

        assert expression_rep(expression) == expression_rep(expression_copy), "Deriv should not mutate expression!"
        good_type = isinstance(result, lab.Expr)
        assert good_type is True, f'Deriv returned unexpected type!\n'+make_err_message()
        assert expression_rep(result) == expression_rep(expect), f'Deriv result != expected after performing:\n' + make_err_message()


def test_deriv_00():
    expression = lab.Num(0)
    expression_copy = lab.Num(0)
    expected = [lab.Num(0), lab.Num(0), lab.Num(0), lab.Num(0), lab.Num(0)]
    _check_deriv(expression, expression_copy, expected)

    sub_expr = lab.Add(lab.Var("x"), lab.Num(5))

    result = lab.Add(sub_expr, sub_expr).deriv("x")
    expected = lab.Add(lab.Add(lab.Num(1), lab.Num(0)), lab.Add(lab.Num(1), lab.Num(0)))
    good_type = isinstance(result, lab.Expr)
    assert good_type is True, f'Deriv returned unexpected type!\n{result = }'
    passed = expression_rep(result) == expression_rep(expected)
    assert passed is True, f"Incorrect deriv result!\nresult   {str(result)}\nexpected {str(expected)}"

    result = lab.Sub(sub_expr, sub_expr).deriv("x")
    expected = lab.Sub(lab.Add(lab.Num(1), lab.Num(0)), lab.Add(lab.Num(1), lab.Num(0)))
    good_type = isinstance(result, lab.Expr)
    assert good_type is True, f'Deriv returned unexpected type!\n{result = }'
    passed = expression_rep(result) == expression_rep(expected)
    assert passed is True, f"Incorrect deriv result!\nresult   {str(result)}\nexpected {str(expected)}"

    result = lab.Div(lab.Var("x"), lab.Num(5)).deriv("x")
    expected = lab.Div(
        lab.Sub(lab.Mul(lab.Num(5), lab.Num(1)), lab.Mul(lab.Var("x"), lab.Num(0))),
        lab.Mul(lab.Num(5), lab.Num(5)),
    )
    good_type = isinstance(result, lab.Expr)
    assert good_type is True, f'Deriv returned unexpected type!\n{result = }'
    passed = expression_rep(result) == expression_rep(expected)
    assert passed is True, f"Incorrect deriv result!\nresult   {str(result)}\nexpected {str(expected)}"

    result = lab.Mul(lab.Var("x"), lab.Num(5)).deriv("x")
    expected = lab.Add(
        lab.Mul(lab.Num(5), lab.Num(1)), lab.Mul(lab.Var("x"), lab.Num(0))
    )
    good_type = isinstance(result, lab.Expr)
    assert good_type is True, f'Deriv returned unexpected type!\n{result = }'
    passed = expression_rep(result) == expression_rep(expected)
    assert passed is True, f"Incorrect deriv result!\nresult   {str(result)}\nexpected {str(expected)}"

    for i in range(74, 87):
        expression = read_expected(f"{i}_in.pyobj")
        expression_copy = read_expected(f"{i}_in.pyobj")
        expected = read_expected(f"{i}_out.pyobj")
        _check_deriv(expression, expression_copy, expected)


test_deriv_00_types = with_no_type_checks(test_deriv_00, mix_up_symbols=True)

def _check_simplify(expression, expected, expression_copy=None):
    def make_err_message():
        return f'\nresult={repr(expression)}.simply()\n#       result was {repr(result)}\n# but expected was {repr(expected)}'

    result = expression.simplify()
    good_type = isinstance(result, lab.Expr)
    assert good_type is True, f'Simplify returned unexpected type!'+make_err_message()
    if expression_copy:
        assert expression_rep(expression) == expression_rep(expression_copy), f'Simplify should not mutate input!'

    passed = expression_rep(result) == expression_rep(expected)
    assert passed is True, f'Simplify returned incorrect result!' + make_err_message()

def test_simplify_00():
    expected = lab.Var("x")
    expression = lab.Add(lab.Num(0), lab.Var("x"))
    _check_simplify(expression, expected)

    expression = lab.Add(lab.Var("x"), lab.Num(0))
    _check_simplify(expression, expected)

    expression = lab.Mul(lab.Num(1), lab.Var("x"))
    _check_simplify(expression, expected)

    expression = lab.Mul(lab.Var("x"), lab.Num(1))
    _check_simplify(expression, expected)

    expression = lab.Sub(lab.Var("x"), lab.Num(0))
    _check_simplify(expression, expected)

    expression = lab.Div(lab.Var("x"), lab.Num(1))
    _check_simplify(expression, expected)

    expression = lab.Div(lab.Num(0), lab.Var("x"))
    expected = lab.Num(0)
    _check_simplify(expression, expected)

    expression = lab.Add(lab.Num(20), lab.Num(30))
    expected = lab.Num(50)
    _check_simplify(expression, expected)

    expression = lab.Sub(lab.Num(50), lab.Num(80))
    expected = lab.Num(-30)
    _check_simplify(expression, expected)

    expression = lab.Div(lab.Num(40), lab.Num(20))
    expected = lab.Num(2.0)
    _check_simplify(expression, expected)

    expression = lab.Mul(lab.Num(101), lab.Num(121))
    expected = lab.Num(12221)
    _check_simplify(expression, expected)

    expression = lab.Div(lab.Num(2), lab.Num(2))
    expected = lab.Num(1.0)
    _check_simplify(expression, expected)

    expression = lab.Div(lab.Var("x"), lab.Num(0))
    expected = lab.Div(lab.Var("x"), lab.Num(0))
    _check_simplify(expression, expected)

    result = lab.Div(lab.Var("x"), lab.Var("x")).simplify()
    expected = lab.Div(lab.Var("x"), lab.Var("x"))
    assert expression_rep(result) == expression_rep(
        expected
    ), f"Make sure to not oversimplify!\n# Got   {result=}\n# But {expected=}"

    result = lab.Sub(lab.Var("x"), lab.Var("x")).simplify()
    expected = lab.Sub(lab.Var("x"), lab.Var("x"))
    assert expression_rep(result) == expression_rep(
        expected
    ), f"Make sure to not oversimplify!\n# Got   {result=}\n# But {expected=}"

    expression = lab.Sub(lab.Num(0), lab.Var("x"))
    expected = lab.Sub(lab.Num(0), lab.Var("x"))
    _check_simplify(expression, expected)

    result = lab.Add(lab.Var("x"), lab.Var("x")).simplify()
    expected = lab.Add(lab.Var("x"), lab.Var("x"))
    assert expression_rep(result) == expression_rep(
        expected
    ), f"Make sure to not oversimplify!\n# Got   {result=}\n# But {expected=}"

    result = lab.Mul(lab.Var("x"), lab.Var("x")).simplify()
    expected = lab.Mul(lab.Var("x"), lab.Var("x"))
    assert expression_rep(result) == expression_rep(
        expected
    ), f"Make sure to not oversimplify!\n# Got   {result=}\n# But {expected=}"


def test_simplify_01():
    expression_copy = lab.Add(lab.Num(0), lab.Mul(lab.Var("y"), lab.Num(2)))
    expression = lab.Add(lab.Num(0), lab.Mul(lab.Var("y"), lab.Num(2)))
    expected = lab.Mul(lab.Var("y"), lab.Num(2))
    _check_simplify(expression, expected, expression_copy)

    expression_copy = lab.Add(lab.Mul(lab.Var("z"), lab.Num(3)), lab.Num(0))
    expression = lab.Add(lab.Mul(lab.Var("z"), lab.Num(3)), lab.Num(0))
    expected = lab.Mul(lab.Var("z"), lab.Num(3))
    _check_simplify(expression, expected, expression_copy)

    expression_copy = lab.Mul(lab.Num(1), lab.Add(lab.Var("A"), lab.Var("x")))
    expression = lab.Mul(lab.Num(1), lab.Add(lab.Var("A"), lab.Var("x")))
    expected = lab.Add(lab.Var("A"), lab.Var("x"))
    _check_simplify(expression, expected, expression_copy)

    expression_copy = lab.Mul(lab.Sub(lab.Var("x"), lab.Var("A")), lab.Num(1))
    expression = lab.Mul(lab.Sub(lab.Var("x"), lab.Var("A")), lab.Num(1))
    expected = lab.Sub(lab.Var("x"), lab.Var("A"))
    _check_simplify(expression, expected, expression_copy)

    expression_copy = lab.Sub(lab.Mul(lab.Var("x"), lab.Num(3)), lab.Num(0))
    expression = lab.Sub(lab.Mul(lab.Var("x"), lab.Num(3)), lab.Num(0))
    expected = lab.Mul(lab.Var("x"), lab.Num(3))
    _check_simplify(expression, expected, expression_copy)

    expression_copy = lab.Div(lab.Mul(lab.Num(7), lab.Var("A")), lab.Num(1))
    expression = lab.Div(lab.Mul(lab.Num(7), lab.Var("A")), lab.Num(1))
    expected = lab.Mul(lab.Num(7), lab.Var("A"))
    _check_simplify(expression, expected, expression_copy)

    expression_copy = lab.Div(lab.Num(0), lab.Add(lab.Var("A"), lab.Num(3)))
    expression = lab.Div(lab.Num(0), lab.Add(lab.Var("A"), lab.Num(3)))
    expected = lab.Num(0)
    _check_simplify(expression, expected, expression_copy)

    expression_copy = lab.Mul(lab.Add(lab.Num(0), lab.Var("x")), lab.Var("z"))
    expression = lab.Mul(lab.Add(lab.Num(0), lab.Var("x")), lab.Var("z"))
    expected = lab.Mul(lab.Var("x"), lab.Var("z"))
    _check_simplify(expression, expected, expression_copy)

    expression_copy = lab.Sub(lab.Add(lab.Var("x"), lab.Num(0)), lab.Var("A"))
    expression = lab.Sub(lab.Add(lab.Var("x"), lab.Num(0)), lab.Var("A"))
    expected = lab.Sub(lab.Var("x"), lab.Var("A"))
    _check_simplify(expression, expected, expression_copy)

    expression_copy = lab.Add(lab.Mul(lab.Num(1), lab.Var("x")), lab.Var("y"))
    expression = lab.Add(lab.Mul(lab.Num(1), lab.Var("x")), lab.Var("y"))
    expected = lab.Add(lab.Var("x"), lab.Var("y"))
    _check_simplify(expression, expected, expression_copy)

    expression_copy = lab.Add(lab.Var("z"), lab.Mul(lab.Var("x"), lab.Num(1)))
    expression = lab.Add(lab.Var("z"), lab.Mul(lab.Var("x"), lab.Num(1)))
    expected = lab.Add(lab.Var("z"), lab.Var("x"))
    _check_simplify(expression, expected, expression_copy)

    expression_copy = lab.Sub(lab.Var("A"), lab.Sub(lab.Var("x"), lab.Num(0)))
    expression = lab.Sub(lab.Var("A"), lab.Sub(lab.Var("x"), lab.Num(0)))
    expected = lab.Sub(lab.Var("A"), lab.Var("x"))
    _check_simplify(expression, expected, expression_copy)

    expression_copy = lab.Div(lab.Var("y"), lab.Div(lab.Var("x"), lab.Num(1)))
    expression = lab.Div(lab.Var("y"), lab.Div(lab.Var("x"), lab.Num(1)))
    expected = lab.Div(lab.Var("y"), lab.Var("x"))
    _check_simplify(expression, expected, expression_copy)

    expression_copy = lab.Mul(lab.Var("z"), lab.Div(lab.Num(0), lab.Var("x")))
    expression = lab.Mul(lab.Var("z"), lab.Div(lab.Num(0), lab.Var("x")))
    expected = lab.Num(0)
    _check_simplify(expression, expected, expression_copy)

    expression_copy = lab.Add(lab.Mul(lab.Num(0), lab.Var("y")), lab.Var("x"))
    expression = lab.Add(lab.Mul(lab.Num(0), lab.Var("y")), lab.Var("x"))
    expected = lab.Var("x")
    _check_simplify(expression, expected, expression_copy)

    expression_copy = lab.Add(lab.Var("x"), lab.Sub(lab.Num(2), lab.Num(2)))
    expression = lab.Add(lab.Var("x"), lab.Sub(lab.Num(2), lab.Num(2)))
    expected = lab.Var("x")
    _check_simplify(expression, expected, expression_copy)

    expression_copy = lab.Mul(lab.Div(lab.Num(2), lab.Num(2)), lab.Var("x"))
    expression = lab.Mul(lab.Div(lab.Num(2), lab.Num(2)), lab.Var("x"))
    expected = lab.Var("x")
    _check_simplify(expression, expected, expression_copy)

    expression_copy = lab.Mul(lab.Var("x"), lab.Sub(lab.Num(3), lab.Num(2)))
    expression = lab.Mul(lab.Var("x"), lab.Sub(lab.Num(3), lab.Num(2)))
    expected = lab.Var("x")
    _check_simplify(expression, expected, expression_copy)

    expression_copy = lab.Sub(lab.Var("x"), lab.Mul(lab.Num(0), lab.Var("z")))
    expression = lab.Sub(lab.Var("x"), lab.Mul(lab.Num(0), lab.Var("z")))
    expected = lab.Var("x")
    _check_simplify(expression, expected, expression_copy)

    expression_copy = lab.Div(lab.Var("x"), lab.Num(1))
    expression = lab.Div(lab.Var("x"), lab.Num(1))
    expected = lab.Var("x")
    _check_simplify(expression, expected, expression_copy)

    expression_copy = lab.Div(lab.Add(lab.Num(0), lab.Num(0)), lab.Var("x"))
    expression = lab.Div(lab.Add(lab.Num(0), lab.Num(0)), lab.Var("x"))
    expected = lab.Num(0)
    _check_simplify(expression, expected, expression_copy)

    expression_copy = lab.Sub(lab.Add(lab.Num(70), lab.Num(50)), lab.Num(80))
    expression = lab.Sub(lab.Add(lab.Num(70), lab.Num(50)), lab.Num(80))
    expected = lab.Num(40)
    _check_simplify(expression, expected, expression_copy)

    expression_copy = lab.Sub(lab.Num(80), lab.Div(lab.Num(40), lab.Num(20)))
    expression = lab.Sub(lab.Num(80), lab.Div(lab.Num(40), lab.Num(20)))
    expected = lab.Num(78.0)
    _check_simplify(expression, expected, expression_copy)



def test_simplify_02():
    expression_copy = lab.Sub(lab.Num(1), lab.Var("L"))
    expression = lab.Sub(lab.Num(1), lab.Var("L"))
    expected = lab.Sub(lab.Num(1), lab.Var("L"))
    _check_simplify(expression, expected, expression_copy)

    expression_copy = lab.Add(lab.Var("b"), lab.Num(1))
    expression = lab.Add(lab.Var("b"), lab.Num(1))
    expected = lab.Add(lab.Var("b"), lab.Num(1))
    _check_simplify(expression, expected, expression_copy)

    expression_copy = lab.Div(lab.Var("M"), lab.Var("D"))
    expression = lab.Div(lab.Var("M"), lab.Var("D"))
    expected = lab.Div(lab.Var("M"), lab.Var("D"))
    _check_simplify(expression, expected, expression_copy)

    expression_copy = lab.Div(lab.Add(lab.Num(1), lab.Var("Q")), lab.Var("k"))
    expression = lab.Div(lab.Add(lab.Num(1), lab.Var("Q")), lab.Var("k"))
    expected = lab.Div(lab.Add(lab.Num(1), lab.Var("Q")), lab.Var("k"))
    _check_simplify(expression, expected, expression_copy)

    for i in range(123, 138):
        expression_copy = read_expected(f"{i}_in.pyobj")
        expression = read_expected(f"{i}_in.pyobj")
        expected = read_expected(f"{i}_out.pyobj")
        _check_simplify(expression, expected, expression_copy)


test_simplify_00_types = with_no_type_checks(test_simplify_00, mix_up_symbols=True)
test_simplify_01_types = with_no_type_checks(test_simplify_01, mix_up_symbols=True)
test_simplify_02_types = with_no_type_checks(test_simplify_02, mix_up_symbols=True)


def test_make_expression_00():
    result = lab.make_expression("x")
    expected = lab.Var("x")
    passed = expression_rep(result) == expression_rep(expected)
    assert passed is True

    result = lab.make_expression("20")
    expected = lab.Num(20)
    passed = expression_rep(result) == expression_rep(expected)
    assert passed is True

    result = lab.make_expression("6.1010")
    expected = lab.Num(6.1010)
    passed = expression_rep(result) == expression_rep(expected)
    assert passed is True

    result = lab.make_expression("-4.9")
    expected = lab.Num(-4.9)
    passed = expression_rep(result) == expression_rep(expected)
    assert passed is True

    result = lab.make_expression("(0 + x)")
    expected = lab.Add(lab.Num(0), lab.Var("x"))
    passed = expression_rep(result) == expression_rep(expected)
    assert passed is True

    result = lab.make_expression("(-101 * x)")
    expected = lab.Mul(lab.Num(-101), lab.Var("x"))
    passed = expression_rep(result) == expression_rep(expected)
    assert passed is True

    result = lab.make_expression("(x + (-.5 / x))")
    expected = lab.Add(lab.Var("x"), lab.Div(lab.Num(-0.5), lab.Var("x")))
    passed = expression_rep(result) == expression_rep(expected)
    assert passed is True

    result = lab.make_expression("(y * -2)")
    expected = lab.Mul(lab.Var("y"), lab.Num(-2))
    passed = expression_rep(result) == expression_rep(expected)
    assert passed is True

    result = lab.make_expression("((z * 3) + 0)")
    expected = lab.Add(lab.Mul(lab.Var("z"), lab.Num(3)), lab.Num(0))
    passed = expression_rep(result) == expression_rep(expected)
    assert passed is True

    result = lab.make_expression("((7 * A) / 9)")
    expected = lab.Div(lab.Mul(lab.Num(7), lab.Var("A")), lab.Num(9))
    passed = expression_rep(result) == expression_rep(expected)
    assert passed is True

    result = lab.make_expression("(z + (x + 1))")
    expected = lab.Add(lab.Var("z"), lab.Add(lab.Var("x"), lab.Num(1)))
    passed = expression_rep(result) == expression_rep(expected)
    assert passed is True

    result = lab.make_expression("(A - (x + A))")
    expected = lab.Sub(lab.Var("A"), lab.Add(lab.Var("x"), lab.Var("A")))
    passed = expression_rep(result) == expression_rep(expected)
    assert passed is True

    result = lab.make_expression("(y / (x / z))")
    expected = lab.Div(lab.Var("y"), lab.Div(lab.Var("x"), lab.Var("z")))
    passed = expression_rep(result) == expression_rep(expected)
    assert passed is True

    result = lab.make_expression("((x * y) * z)")
    expected = lab.Mul(lab.Mul(lab.Var("x"), lab.Var("y")), lab.Var("z"))
    passed = expression_rep(result) == expression_rep(expected)
    assert passed is True

    result = lab.make_expression("((x + A) * (y + z))")
    expected = read_expected("187_out.pyobj")
    passed = expression_rep(result) == expression_rep(expected)
    assert passed is True


def test_make_expression_01():
    result = lab.make_expression(read_expected("188_in.pyobj"))
    expected = read_expected("188_out.pyobj")
    passed = expression_rep(result) == expression_rep(expected)
    assert passed is True

    result = lab.make_expression(read_expected("189_in.pyobj"))
    expected = read_expected("189_out.pyobj")
    passed = expression_rep(result) == expression_rep(expected)
    assert passed is True

    result = lab.make_expression(read_expected("190_in.pyobj"))
    expected = read_expected("190_out.pyobj")
    passed = expression_rep(result) == expression_rep(expected)
    assert passed is True

    result = lab.make_expression(read_expected("191_in.pyobj"))
    expected = read_expected("191_out.pyobj")
    passed = expression_rep(result) == expression_rep(expected)
    assert passed is True


# TESTING UTILS DO NOT MODIFY!
from collections import OrderedDict

_unprep_funcs = {
    "OrderedDict": OrderedDict,
    "frozenset": frozenset,
    "set": set,
}
for i in ("Add", "Sub", "Mul", "Div", "Var", "Num"):
    _a = getattr(lab, i, None)
    if _a is not None:
        _unprep_funcs[i] = _a


def safe_eval(node_or_string):
    original_node_or_string = node_or_string
    if iisinstance(node_or_string, str):
        node_or_string = ast.parse(node_or_string, mode="eval")
    if iisinstance(node_or_string, ast.Expression):
        node_or_string = node_or_string.body

    def _convert(node):
        if iisinstance(node, (ast.Constant)):
            return node.value
        elif iisinstance(node, ast.Tuple):
            return tuple(map(_convert, node.elts))
        elif iisinstance(node, ast.List):
            return list(map(_convert, node.elts))
        elif iisinstance(node, ast.Set):
            return set(map(_convert, node.elts))
        elif iisinstance(node, ast.Dict):
            return dict(
                (_convert(k), _convert(v)) for k, v in zip(node.keys, node.values)
            )
        elif iisinstance(node, ast.Constant):
            return node.value
        elif (
            iisinstance(node, ast.UnaryOp)
            and iisinstance(node.op, (ast.UAdd, ast.USub))
            and iisinstance(node.operand, (ast.Constant, ast.UnaryOp, ast.BinOp))
        ):
            operand = _convert(node.operand)
            if iisinstance(node.op, ast.UAdd):
                return +operand
            else:
                return -operand
        elif (
            iisinstance(node, ast.BinOp)
            and iisinstance(node.op, (ast.Add, ast.Sub))
            and iisinstance(node.right, (ast.Constant, ast.UnaryOp, ast.BinOp))
            and iisinstance(node.left, (ast.Constant, ast.UnaryOp, ast.BinOp))
        ):
            left = _convert(node.left)
            right = _convert(node.right)
            if iisinstance(node.op, ast.Add):
                return left + right
            else:
                return left - right
        elif (
            iisinstance(node, ast.Call)
            and iisinstance(node.func, ast.Name)
            and node.func.id in _unprep_funcs
        ):
            return _unprep_funcs[node.func.id](*(_convert(i) for i in node.args))
        elif (
            iisinstance(node, ast.Call)
            and iisinstance(node.func, ast.Attribute)
            and node.func.attr in _unprep_funcs
        ):
            return _unprep_funcs[node.func.attr](*(_convert(i) for i in node.args))
        raise ValueError(f"malformed node or string:\n{original_node_or_string}")

    return _convert(node_or_string)


# read in expected result
def read_expected(fname):
    with open(os.path.sep.join([TEST_DIRECTORY, "testing_data", fname]), "r") as f:
        return safe_eval(f.read())
