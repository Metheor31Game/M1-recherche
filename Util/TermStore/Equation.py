from Util.TermStore.terme import NoeudTerme

class Equation:
    """
    Représente une équation entre deux termes à unifier.
    
    Attributes:
        left (NodeTerm): Le terme gauche de l'équation.
        right (NodeTerm): Le terme droit de l'équation.
    
    Example:
        >>> eq = Equation(TermFactory.create_var("X"), TermFactory.create_const("a"))
        >>> # Représente l'équation X = a
    """
    def __init__(self, left: NoeudTerme, right: NoeudTerme):
        self.left = left
        self.right = right