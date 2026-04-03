from abc import ABC, abstractmethod


class TermeAbstrait(ABC):
    """
    Classe abstraite définissant l'interface commune à toutes les
    représentations de termes logiques du premier ordre.

    Un "terme" au sens de cette interface peut représenter :
        - un terme logique classique : f(X, g(a))
        - un littéral entier         : P(f(X), a)  où P est le prédicat racine

   
    Structures implémentant cette interface :
        - TermeArbre : représentation par arbre
        - TermeDict  : représentation par dictionnaire plat
        - TermeListe : représentation par liste
    """

    @property
    @abstractmethod
    def nom(self):
        """
        Nom du symbole racine.
        Pour un littéral P(f(X), a) : retourne "P"
        Pour un terme f(X, a)       : retourne "f"
        """
        pass

    @property
    @abstractmethod
    def typeNoeud(self):
        """
        Type du noeud racine.
        Valeurs possibles : "var", "cons", "fonc", "pred"
        "pred" est utilisé quand la racine est un prédicat.
        """
        pass

    @property
    @abstractmethod
    def arite(self):
        """
        Arité du noeud racine.
        Pour P(f(X), a) : retourne 2
        Pour f(X)       : retourne 1
        Pour X ou a     : retourne 0
        """
        pass

    @property
    @abstractmethod
    def enfants(self):
        """
        Liste des sous-termes enfants.

        """
        pass

    @abstractmethod
    def getVariables(self):
        """
        Retourne l'ensemble des noms de variables présentes dans le terme.

        Ex : P(f(X), g(Y)) → {"X", "Y"}

        Returns:
            set : ensemble des noms de variables
        """
        pass

    @abstractmethod
    def substituer(self, nom_var: str, remplacement: "TermeAbstrait") -> "TermeAbstrait":
        """
        Retourne un nouveau terme où toutes les occurrences de nom_var
        ont été remplacées par remplacement.

        Args:
            nom_var   	          : nom de la variable à remplacer
            remplacement (TermeAbstrait) : terme de remplacement
        Returns:
            TermeAbstrait : nouveau terme après substitution
        """
        pass

    @abstractmethod
    def __eq__(self, autre: object):
        """Comparaison structurelle de deux termes."""
        pass

    @abstractmethod
    def __repr__(self):
        """
        Représentation lisible.
        Pour un littéral : P(f(X), a)
        Pour un terme    : f(X, a)
        """
        pass