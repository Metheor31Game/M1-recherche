from typing import Optional, List
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from Util.TermStore.terme import NoeudTerme

"""
Proposition pour littéraux : 
Predicat (nom)
arité
[termes]
signe

Litteral("P", [t1, t2], True)

"""

class Litteral:
    """
    Représente un littéral comme un arbre.
    La racine est le prédicat (avec son signe), les enfants sont les termes.
    
    Structure :
        +P (arity = 2)
        ├── t1
        └── t2
    """
    def __init__(self, predicat: str, enfants: List[NoeudTerme], sign: bool = True):
        self.predicat = predicat
        self.enfants = enfants  # les termes sont les enfants du nœud
        self.sign = sign
        self.arity = len(enfants)

    def __repr__(self):
        """
        Représente un littéral sous la forme compacte : +P(t1, t2)
        """
        terms_str = ", ".join(repr(t) for t in self.enfants)
        signe = "+" if self.sign else "-"
        return f"{signe}{self.predicat}({terms_str})"
    
    def afficher_arbre(self, indent: str = "", est_dernier: bool = True) -> str:
        """
        Représente le littéral sous forme d'arbre avec ses termes comme enfants.
        Affiche récursivement la structure complète du littéral.
        
        Args:
            indent (str): Indentation courante pour l'affichage (utilisé en interne).
            est_dernier (bool): Indique si c'est le dernier enfant (utilisé en interne).
        
        Returns:
            str: Représentation arborescente du littéral.
        
        Example:
            >>> X = FabriqueDeTermes.creer_var("X")
            >>> a = FabriqueDeTermes.creer_cons("a")
            >>> f_X_a = FabriqueDeTermes.creer_fonc("f", 2, [X, a])
            >>> Y = FabriqueDeTermes.creer_var("Y")
            >>> lit = Litteral("P", [f_X_a, Y], True)
            >>> print(lit.afficher_arbre())
            +P (arity = 2)
            ├── f (arity = 2)
            │   ├── X (var)
            │   └── a (const)
            └── Y (var)
        """
        signe = "+" if self.sign else "-"
        lines = [f"{indent}{signe}{self.predicat} (arity = {self.arity})"]
        
        for i, enfant in enumerate(self.enfants):
            est_dernier_enfant = (i == len(self.enfants) - 1)
            branche = "└── " if est_dernier_enfant else "├── "
            sous_indent = "    " if est_dernier_enfant else "│   "
            
            # Afficher le terme (qui est lui-même un arbre)
            lines.append(self._afficher_terme(enfant, indent + branche, indent + sous_indent))
        
        return "\n".join(lines)
    
    def _afficher_terme(self, terme: NoeudTerme, prefixe: str, indent: str) -> str:
        """
        Affiche un terme récursivement sous forme d'arbre.
        """
        # Racine du terme
        if terme.etiquette in ["const", "var"]:
            return f"{prefixe}{terme.nom} ({terme.etiquette})"
        else:
            lines = [f"{prefixe}{terme.nom} (arity = {terme.etiquette})"]
            for i, enfant in enumerate(terme.enfants):
                est_dernier = (i == len(terme.enfants) - 1)
                branche = "└── " if est_dernier else "├── "
                sous_indent = "    " if est_dernier else "│   "
                lines.append(self._afficher_terme(enfant, indent + branche, indent + sous_indent))
            return "\n".join(lines)
        