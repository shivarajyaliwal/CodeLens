import ast
from dataclasses import dataclass
from typing import List


@dataclass
class ExplanationResult:
    summary: str
    step_by_step: List[str]
    complexity: str
    alternatives: List[str]
    ast_outline: List[str]


class CodeAnalyzer(ast.NodeVisitor):
    def __init__(self) -> None:
        self.steps: List[str] = []
        self.outline: List[str] = []
        self.loop_depth = 0
        self.max_loop_depth = 0
        self.has_recursion = False
        self._function_stack: List[str] = []

    def _push_outline(self, node: ast.AST, label: str) -> None:
        line = getattr(node, "lineno", "?")
        self.outline.append(f"L{line}: {label}")

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._function_stack.append(node.name)
        self.steps.append(f"Define function `{node.name}` with {len(node.args.args)} parameter(s).")
        self._push_outline(node, f"FunctionDef {node.name}")
        self.generic_visit(node)
        self._function_stack.pop()

    def visit_For(self, node: ast.For) -> None:
        self.loop_depth += 1
        self.max_loop_depth = max(self.max_loop_depth, self.loop_depth)
        target = ast.unparse(node.target) if hasattr(ast, "unparse") else "loop variable"
        source = ast.unparse(node.iter) if hasattr(ast, "unparse") else "iterable"
        self.steps.append(f"For-loop iterates `{target}` over `{source}`.")
        self._push_outline(node, "For loop")
        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_While(self, node: ast.While) -> None:
        self.loop_depth += 1
        self.max_loop_depth = max(self.max_loop_depth, self.loop_depth)
        condition = ast.unparse(node.test) if hasattr(ast, "unparse") else "condition"
        self.steps.append(f"While-loop continues while `{condition}` is true.")
        self._push_outline(node, "While loop")
        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_If(self, node: ast.If) -> None:
        condition = ast.unparse(node.test) if hasattr(ast, "unparse") else "condition"
        self.steps.append(f"Branch checks whether `{condition}`.")
        self._push_outline(node, "If branch")
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        if node.targets:
            target = ast.unparse(node.targets[0]) if hasattr(ast, "unparse") else "variable"
            value = ast.unparse(node.value) if hasattr(ast, "unparse") else "value"
            self.steps.append(f"Assign `{value}` into `{target}`.")
        self._push_outline(node, "Assignment")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        fn_name = ast.unparse(node.func) if hasattr(ast, "unparse") else "function"
        self.steps.append(f"Call `{fn_name}`.")
        if self._function_stack and fn_name == self._function_stack[-1]:
            self.has_recursion = True
        self._push_outline(node, f"Call {fn_name}")
        self.generic_visit(node)


def infer_complexity(max_loop_depth: int, has_recursion: bool) -> str:
    if has_recursion and max_loop_depth >= 1:
        return "Potentially super-linear complexity due to recursion inside iterative control flow."
    if has_recursion:
        return "Recursive complexity depends on branching factor and recursion depth (often O(log n) to O(2^n))."
    if max_loop_depth <= 0:
        return "Likely O(1) to O(n), depending on input-size-dependent operations."
    if max_loop_depth == 1:
        return "Likely O(n) time with a single dominant loop."
    if max_loop_depth == 2:
        return "Likely O(n²) time due to nested loops."
    return f"Likely O(n^{max_loop_depth}) time due to loop nesting depth {max_loop_depth}."


def suggest_alternatives(code: str, max_loop_depth: int) -> List[str]:
    suggestions: List[str] = []
    lowered = code.lower()

    if "sort(" in lowered and "for" in lowered:
        suggestions.append("Use built-in sorting (`sorted` / `.sort`) instead of manual loop-based sorting for clarity and performance.")
    if max_loop_depth >= 2:
        suggestions.append("Consider reducing nested loops via hash maps or precomputed indexes to improve time complexity.")
    if "while" in lowered and "len(" in lowered:
        suggestions.append("If index-based scanning is used, consider iterator-based loops for readability.")
    if not suggestions:
        suggestions.append("No obvious structural optimization detected; focus on naming, comments, and edge-case handling.")

    return suggestions


def explain_code(code: str) -> ExplanationResult:
    tree = ast.parse(code)
    analyzer = CodeAnalyzer()
    analyzer.visit(tree)

    summary = "This code was parsed into an AST and explained construct-by-construct."
    complexity = infer_complexity(analyzer.max_loop_depth, analyzer.has_recursion)
    alternatives = suggest_alternatives(code, analyzer.max_loop_depth)

    return ExplanationResult(
        summary=summary,
        step_by_step=analyzer.steps or ["No executable statements detected."],
        complexity=complexity,
        alternatives=alternatives,
        ast_outline=analyzer.outline or ["No AST nodes detected."],
    )
