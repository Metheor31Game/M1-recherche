from Util.TermStore.terme import NoeudTerme, FabriqueDeTermes, ETIQUETTE_VAR, ETIQUETTE_CONS
from Util.Litteral import Litteral
from .TermeAbstrait import TermeAbstrait

TYPE_FONC = "fonc"
TYPE_PRED = "pred"


class TermeArbre(TermeAbstrait):
    """
    Représentation d'un terme ou d'un littéral sous forme d'arbre.

    Deux usages possibles :
      1. Depuis un NoeudTerme (terme : f(X, a))
         → utiliser depuis_noeud()
      2. Depuis un Litteral   (littéral : P(f(X), a))
         → utiliser depuis_litteral()
         Le prédicat P devient le noeud racine, les termes sont les enfants.


    Attributes:
        _nom     (str)  : nom du symbole racine (prédicat, fonction, var, cons)
        _type    (str)  : type du noeud racine
        _arite   (int)  : arité du noeud racine
        _enfants (list) : enfants comme liste de TermeArbre
    """

    def __init__(self, nom: str, type_: str, arite: int, enfants: list):
        self._nom     = nom
        self._type    = type_
        self._arite   = arite
        self._enfants = enfants

    # Propriétés (interface TermeAbstrait)

    @property
    def nom(self):
        return self._nom

    @property
    def typeNoeud(self):
       return self._type 

    @property
    def arite(self) :
        return self._arite

    @property
    def enfants(self):
        return self._enfants

    # Opérations (interface TermeAbstrait)

    def getVariables(self):
        """
        Retourne l'ensemble des noms de variables du terme ou littéral.

        Returns:
            set : ex {"X", "Y"}
        """
        if self._type == ETIQUETTE_VAR:
            return {self._nom}
        if self._type == ETIQUETTE_CONS:
            return set()
        variables = set()
        for enfant in self._enfants:
            variables.update(enfant.getVariables())
        return variables

    def substituer(self, nom_var: str, remplacement: "TermeArbre") -> "TermeArbre":
        """
        Retourne un nouveau TermeArbre où toutes les occurrences
        de nom_var sont remplacées par remplacement.

        Args:
            nom_var      (str)       : nom de la variable à remplacer
            remplacement (TermeArbre): terme de remplacement
        Returns:
            TermeArbre : nouveau terme après substitution
        """
        if nom_var not in self.getVariables():
            return self
        if self._type == ETIQUETTE_VAR:
            return remplacement if self._nom == nom_var else self
        if self._type == ETIQUETTE_CONS:
            return self
        nouveauxEnfants = [
            e.substituer(nom_var, remplacement) for e in self._enfants
        ]
        return TermeArbre(self._nom, self._type, self._arite, nouveauxEnfants)

    # Points d'entrée

    @staticmethod
    def depuis_noeud(noeud: NoeudTerme) -> "TermeArbre":
        """
        Crée un TermeArbre depuis un NoeudTerme existant.
        Pour représenter un terme classique : f(X, a).

        Args:
            noeud (NoeudTerme) : terme issu de Litteral.enfants
        Returns:
            TermeArbre :adaptateur pour MM
        """
        if noeud.etiquette in [ETIQUETTE_VAR, ETIQUETTE_CONS]:
            type_ = noeud.etiquette 
            arite = 0
        else:
            type_ = TYPE_FONC       
            arite = int(noeud.etiquette)
 
        enfants = [TermeArbre.depuis_noeud(e) for e in noeud.enfants]
        return TermeArbre(noeud.nom, type_, arite, enfants)

    @staticmethod
    def depuis_litteral(lit: Litteral) -> "TermeArbre":
        """
        Crée un TermeArbre depuis un Litteral.
        Le prédicat devient le noeud racine (TYPE_PRED),
        les termes du littéral sont les enfants.

        Ex : P(f(X), a) → TermeArbre racine="P"(pred), enfants=[f(X), a]

        Args:
            lit (Litteral) : littéral
        Returns:
            TermeArbre : littéral représenté comme un arbre
        """
        enfants = [TermeArbre.depuis_noeud(t) for t in lit.enfants]
        return TermeArbre(lit.predicat, TYPE_PRED, lit.arity, enfants)

    # Affichage et comparaison

    def __eq__(self, autre: object):
        if not isinstance(autre, TermeArbre):
            return False
        return (self._nom == autre._nom
                and self._type == autre._type
                and self._enfants == autre._enfants)

    def __repr__(self):
        if self._type in [ETIQUETTE_VAR, ETIQUETTE_CONS]:
            return self._nom
        enfants_str = ", ".join(repr(e) for e in self._enfants)
        return f"{self._nom}({enfants_str})"