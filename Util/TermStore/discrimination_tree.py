from typing import List, Dict, Any, Optional
from term import NodeTerm, CONST_TAG, VAR_TAG


class DiscriminationTreeNode:
    """
    A node in the discrimination tree.

    Attributes:
        symbol (Optional[str]): The symbol or variable represented by this node.
                                'None' for the root node.
        children (Dict[str, 'DiscriminationTreeNode']): Child nodes, indexed by their symbol.
        pointers (List[Any]): Pointers to terms associated with this node.
    """
    def __init__(self, symbol: Optional[str] = None) -> None:
        self.symbol = symbol # The symbol that represents the node (e.g. X, f, a, etc.)
        self.children = {} # Child nodes
        self.pointers = [] # Represent terms associated to the node


class DiscriminationTree:
    """Discrimination tree for indexing unifiable terms.
    
    Attributes:
        root ('DiscriminationTreeNode'): Tree's root, 'None' by default
    """
    
    def __init__(self) -> None:
        """Initialize the discrimination tree with an empty root node."""
        self.root = DiscriminationTreeNode()

    def insert(self, term: NodeTerm, pointer: Any) -> None:
        """
        Insert a term into the discrimination tree and associate a pointer with it.
        
        The term is traversed in preorder to create a single path through the tree.
        For example, f(X, g(Y)) creates the path: f -> *1 -> g -> *2

        Args:
            term (NodeTerm): The term to insert into the tree.
            pointer (Any): A pointer to associate with this term.
        """
        var_map = {}
        # Flatten the term into a sequence using preorder traversal
        sequence = self._flatten_term(term, var_map)
        
        # Insert the sequence as a path in the tree
        current_node = self.root
        for symbol in sequence:
            if symbol not in current_node.children:
                current_node.children[symbol] = DiscriminationTreeNode(symbol)
            current_node = current_node.children[symbol]
        
        # Add pointer at the end of the path
        if pointer not in current_node.pointers:
            current_node.pointers.append(pointer)
    
    def _flatten_term(self, term: NodeTerm, var_map: Dict[str, str]) -> List[str]:
        """
        Flatten a term into a sequence of symbols using preorder traversal.
        
        For f(X, g(Y)), returns: ['f', '*1', 'g', '*2']
        
        Args:
            term (NodeTerm): The term to flatten.
            var_map (Dict[str, str]): Variable normalization mapping.
            
        Returns:
            List[str]: Sequence of symbols in preorder.
        """
        result = []
        
        # Add the current symbol
        if term.tag == VAR_TAG:
            if term.name not in var_map:
                var_map[term.name] = f"*{len(var_map) + 1}"
            result.append(var_map[term.name])
        else:
            result.append(term.name)
        
        # Add children recursively (preorder)
        if term.tag not in [CONST_TAG, VAR_TAG]:
            for child in term.children:
                result.extend(self._flatten_term(child, var_map))
        
        return result
    
    def print_tree(self, node: Optional[DiscriminationTreeNode] = None, level: int = 0, prefix: str = "", is_last: bool = True, path: str = "") -> None:
        """Print the tree structure.
        
        Args:
            node (Optional['DiscriminationTreeNode']): The node to print, usefull for recursive printing, 'None' by default.
            level (int): Current level in the tree, used for indentation.
            prefix (str): Prefix string for formatting the tree structure.
            is_last (bool): Whether the current node is the last child of its parent.
            path (str): The path to the current node.
        """
        if node is None:
            # Starting at the root
            node = self.root
            print("╔" + "═" * 58 + "╗")
            print("║" + " " * 16 + "DISCRIMINATION TREE" + " " * 23 + "║")
            print("╚" + "═" * 58 + "╝")
            print("\nROOT")
            children_list = list(node.children.values())
            for i, child_node in enumerate(children_list):
                is_last_child = (i == len(children_list) - 1)
                self.print_tree(child_node, level + 1, "", is_last_child, child_node.symbol)
            return
        
        # Determine the connector symbols
        connector = "└── " if is_last else "├── "
        extension = "    " if is_last else "│   "
        
        # Display the current node with path information
        symbol_display = node.symbol
        
        if node.pointers:
            # Leaf node with pointers
            print(f"{prefix}{connector}[{symbol_display}]")
            for i, pointer in enumerate(node.pointers):
                is_last_pointer = (i == len(node.pointers) - 1)
                pointer_connector = "    └─→ " if is_last_pointer else "    ├─→ "
                pointer_prefix = prefix + extension if not is_last else prefix + "    "
                print(f"{pointer_prefix}{pointer_connector}{pointer}")
        else:
            # Internal node
            print(f"{prefix}{connector}{symbol_display}")
        
        # Process children
        children_list = list(node.children.values())
        for i, child_node in enumerate(children_list):
            is_last_child = (i == len(children_list) - 1)
            child_path = f"{path}/{child_node.symbol}"
            self.print_tree(child_node, level + 1, prefix + extension, is_last_child, child_path)


# Example usage
if __name__ == "__main__":
    from term import TermFactory

    dt = DiscriminationTree()

    # term1: f(X, g(Y))
    term1 = TermFactory.create_func("f", 2, [
        TermFactory.create_var("X"),
        TermFactory.create_func("g", 1, [TermFactory.create_var("Y")])
    ])
    
    # term2: f(Z, g(W)) - identical to term1 modulo variable renaming
    term2 = TermFactory.create_func("f", 2, [
        TermFactory.create_var("Z"),
        TermFactory.create_func("g", 1, [TermFactory.create_var("W")])
    ])
    
    # term3: f(a, g(b)) - concrete instance
    term3 = TermFactory.create_func("f", 2, [
        TermFactory.create_const("a"),
        TermFactory.create_func("g", 1, [TermFactory.create_const("b")])
    ])
    
    # term4: f(a, g(X)) - partially instantiated
    term4 = TermFactory.create_func("f", 2, [
        TermFactory.create_const("a"),
        TermFactory.create_func("g", 1, [TermFactory.create_var("X")])
    ])
    
    # term5: f(X, Y) - very general
    term5 = TermFactory.create_func("f", 2, [
        TermFactory.create_var("X"),
        TermFactory.create_var("Y")
    ])
    
    # term6: f(Y, X) - opposite of term5
    term6 = TermFactory.create_func("f", 2, [
        TermFactory.create_var("Y"),
        TermFactory.create_var("X")
    ])

    # Insert terms
    dt.insert(term1, "term1: f(X, g(Y))")
    dt.insert(term2, "term2: f(Z, g(W))")
    dt.insert(term3, "term3: f(a, g(b))")
    dt.insert(term4, "term4: f(a, g(X))")
    dt.insert(term5, "term5: f(X, Y)")
    dt.insert(term6, "term6: f(Y, X)")

    # Display
    dt.print_tree()

