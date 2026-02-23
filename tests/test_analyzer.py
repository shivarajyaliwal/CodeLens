from analyzer import explain_code


def test_nested_loops_complexity_hint():
    code = """
def f(items):
    total = 0
    for x in items:
        for y in items:
            total += x * y
    return total
"""
    result = explain_code(code)
    assert "O(n²)" in result.complexity


def test_recursion_detected():
    code = """
def fact(n):
    if n <= 1:
        return 1
    return n * fact(n-1)
"""
    result = explain_code(code)
    assert "Recursive complexity" in result.complexity
