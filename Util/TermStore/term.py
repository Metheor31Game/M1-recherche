import random
from typing import Union, List, Optional

DEFAULT_MAX_DEPTH = 3
DEFAULT_MAX_ARITY = 3
CONST_TAG = "const"
VAR_TAG = "var"
CONSTS_DOMAIN = ['a', 'b', 'c', 'd', 'e']
VARS_DOMAIN = ['U', 'V', 'W','X', 'Y', 'Z']
FUNCTIONS_DOMAIN = ['f', 'g', 'h', 'i', 'j', 'k', 'l']
ARITIES = {
    'f': random.randint(1, DEFAULT_MAX_ARITY),
    'g': random.randint(1, DEFAULT_MAX_ARITY),
    'h': random.randint(1, DEFAULT_MAX_ARITY),
    'i': random.randint(1, DEFAULT_MAX_ARITY),
    'j': random.randint(1, DEFAULT_MAX_ARITY),
    'k': random.randint(1, DEFAULT_MAX_ARITY),
    'l': random.randint(1, DEFAULT_MAX_ARITY),
}

class NodeTerm:
    """
    Class that represents a node in a symbolic term tree.
    Can be a constant, variable, or function with children.

    Attributes:
        name (str): The name of the term (e.g. "a", "X" or "f").
        tag (Union[str, int]): A tag to identify the type of the term, or the arity of a function ("const", "var", or 3 for a function with 3 arguments).
        children (Optional[List['NodeTerm']]): List of child NodeTerm instances if the term is a function.
    """
    def __init__(self, name: str, tag: Union[str, int], children: Optional[List['NodeTerm']] = None):
        self.name = name
        self.tag = tag
        self.children = children if children is not None else []

    def __repr__(self) -> str:
        if self.tag in [CONST_TAG, VAR_TAG]:
            return f"{self.name}"
        else:
            children_repr = ", ".join(repr(child) for child in self.children)
            return f"{self.name}({children_repr})"
        
        
class TermFactory:
    """
    Utility class for creating NodeTerm instances representing constants, variables, and functions.
    """
    @staticmethod
    def create_const(name: str) -> NodeTerm:
        return NodeTerm(name=name, tag=CONST_TAG)
     
    @staticmethod
    def create_var(name: str) -> NodeTerm:
        return NodeTerm(name=name, tag=VAR_TAG)
    
    @staticmethod
    def create_func(name: str, arity: int, children: list) -> NodeTerm:
        return NodeTerm(name=name, tag=arity, children=children)

class RandomTermGenerator:
    """
    Class for generating random symbolic terms.

    Attributes:
        max_depth (int): Maximum depth of the generated term tree (3 by default).
        max_arity (int): Maximum arity of functions in the generated term tree (3 by default).
    """
    def __init__(self, max_depth: int = DEFAULT_MAX_DEPTH, max_arity: int = DEFAULT_MAX_ARITY):
        self.max_depth = max_depth
        self.max_arity = max_arity
        self.consts = CONSTS_DOMAIN
        self.vars = VARS_DOMAIN
        self.funcs = FUNCTIONS_DOMAIN

    def generate_random_term(self, current_depth: int = 0) -> NodeTerm:
        if current_depth >= self.max_depth:
            # if maximal depth is reached, need to generate constant or variable
            return random.choice([
                self._generate_const(current_depth),
                self._generate_var(current_depth)
            ])
        else:
            # else, we can generate function
            choices = [
                self._generate_const,
                self._generate_var,
                self._generate_func
            ]
            weights = [0.3, 0.3, 0.4] # weights to favorize functions    
            chosen_generator = random.choices(choices, weights=weights)[0]
            return chosen_generator(current_depth)
        
    def _generate_const(self, _:int) -> NodeTerm:
        return TermFactory.create_const(random.choice(self.consts))
    
    def _generate_var(self, _:int) -> NodeTerm:
        return TermFactory.create_var(random.choice(self.vars))
    
    def _generate_func(self, current_depth: int) -> NodeTerm:
        name = random.choice(self.funcs)
        arity = ARITIES.get(name)
        if arity is None:
            arity = 1
        children = [self.generate_random_term(current_depth + 1) for _ in range(arity)]
        return TermFactory.create_func(name, arity, children)
    
    def generate_terms(self, n: int) -> List[NodeTerm]:
        return [self.generate_random_term() for _ in range(n)]
    
generator = RandomTermGenerator(max_depth=3, max_arity=3)
random_terms = generator.generate_terms(10)
for term in random_terms:
    print(term)