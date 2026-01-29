from .term import NodeTerm
from typing import List

class Equation:
    def __init__(self, left: NodeTerm, right: NodeTerm):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"{self.left} = {self.right}"


class TermSystem:
    def __init__(self, equations: List[Equation] = None):
        self.equations = equations if equations is not None else []

    def add(self, left: NodeTerm, right: NodeTerm):
        self.equations.append(Equation(left, right))

    def is_empty(self) -> bool:
        return len(self.equations) == 0

    def __repr__(self):
        return "{ " + ", ".join(repr(eq) for eq in self.equations) + " }"
