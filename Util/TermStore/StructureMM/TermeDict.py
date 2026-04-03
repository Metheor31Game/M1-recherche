from typing import Dict, List
from Util.TermStore.terme import NoeudTerme, ETIQUETTE_VAR, ETIQUETTE_CONS
from Util.Litteral import Litteral
from .TermeAbstrait import TermeAbstrait


TYPE_FONC = "fonc"
TYPE_PRED = "pred"


class TermeDict(TermeAbstrait):
    """
    Représentation d'un terme ou d'un littéral sous forme de dictionnaire plat.

    Tous les nœuds sont stockés dans un dictionnaire plat { id (int) -> dict }.
    On accède à n'importe quel noeud par son id.

    Deux usages possibles :
      1. Depuis un NoeudTerme (terme classique : f(X, a))
         → utiliser depuis_noeud()
      2. Depuis un Litteral   (littéral : P(f(X), a))
         → utiliser depuis_litteral()
         Le prédicat devient le noeud racine (TYPE_PRED, id=0).

    Structure d'un noeud :
        {
            "nom"     : str        — nom du symbole
            "type"    : str        — ETIQUETTE_VAR | ETIQUETTE_CONS | TYPE_FONC | TYPE_PRED
            "arite"   : int        — 0 pour var/cons, n pour fonc/pred
            "enfants" : List[int]  — ids des noeuds enfants
        }

    Exemple — P(f(X), a) :
        racine = 0
        noeuds = {
            0: {"nom": "P", "type": "pred", "arite": 2, "enfants": [1, 3]},
            1: {"nom": "f", "type": "fonc", "arite": 1, "enfants": [2]},
            2: {"nom": "X", "type": "var",  "arite": 0, "enfants": []},
            3: {"nom": "a", "type": "cons", "arite": 0, "enfants": []}
        }

    Attributes:
        _noeuds   (Dict[int, dict]) : tous les noeuds indexés par id
        _racine   (int)             : id du noeud racine
        _compteur (int)             : compteur interne pour les ids
    """

    def __init__(self, noeuds: Dict[int, dict], racine: int, compteur: int):
        self._noeuds   = noeuds
        self._racine   = racine
        self._compteur = compteur

    # Propriétés (interface TermeAbstrait)

    @property
    def nom(self) -> str:
        return self._noeuds[self._racine]["nom"]

    @property
    def typeNoeud(self) -> str:
        return self._noeuds[self._racine]["type"]

    @property
    def arite(self) -> int:
        return self._noeuds[self._racine]["arite"]

    @property
    def enfants(self) -> list:
        """Retourne les enfants comme liste de TermeDict."""
        return [
            TermeDict(self._noeuds, enfant_id, self._compteur)
            for enfant_id in self._noeuds[self._racine]["enfants"]
        ]

    # Opérations (interface TermeAbstrait)

    def getVariables(self) -> set:
        """
        Retourne l'ensemble des noms de variables du terme ou littéral.

        Returns:
            set : ex {"X", "Y"}
        """
    def getVariables(self) -> set:
        variables = set()
        for noeud in self._noeuds.values():
            if noeud["type"] == ETIQUETTE_VAR:
                variables.add(noeud["nom"])
        return variables

    def substituer(self, nom_var: str, remplacement: "TermeDict") -> "TermeDict":
        """
        Retourne un nouveau TermeDict où toutes les occurrences
        de nom_var sont remplacées par remplacement.


        Args:
            nom_var      (str)      : nom de la variable à remplacer
            remplacement (TermeDict): terme de remplacement
        Returns:
            TermeDict : nouveau terme après substitution
        """
        if nom_var not in self.getVariables():
            return self

        nouveaux_noeuds = {}
        compteur = [0]

        def _copier_et_substituer(id_source: int) -> int:
            noeud     = self._noeuds[id_source]
            nouvel_id = compteur[0]
            compteur[0] += 1

            if noeud["type"] == ETIQUETTE_VAR:
                if noeud["nom"] == nom_var:
                    decalage = compteur[0] - remplacement._racine
                    for ancien_id, n in remplacement._noeuds.items():
                        nouvel_id_remp = ancien_id + decalage
                        nouveaux_noeuds[nouvel_id_remp] = {
                            **n,
                            "enfants": [e + decalage for e in n["enfants"]]
                        }
                        compteur[0] = max(compteur[0], nouvel_id_remp + 1)
                    return remplacement._racine + decalage
                else:
                    nouveaux_noeuds[nouvel_id] = {**noeud}
                    return nouvel_id

            elif noeud["type"] == ETIQUETTE_CONS:
                nouveaux_noeuds[nouvel_id] = {**noeud}
                return nouvel_id

            else: 
                nouveaux_enfants = [
                    _copier_et_substituer(e) for e in noeud["enfants"]
                ]
                nouveaux_noeuds[nouvel_id] = {
                    **noeud,
                    "enfants": nouveaux_enfants
                }
                return nouvel_id

        nouvelle_racine = _copier_et_substituer(self._racine)
        return TermeDict(nouveaux_noeuds, nouvelle_racine, compteur[0])

    # Points d'entrée

    @staticmethod
    def depuis_noeud(noeud: NoeudTerme) -> "TermeDict":
        """
        Construit un TermeDict depuis un NoeudTerme existant.
        Pour représenter un terme classique : f(X, a).

        Args:
            noeud (NoeudTerme) : terme issu de Litteral.enfants
        Returns:
            TermeDict : même terme sous forme de dictionnaire plat
        """
        noeuds: Dict[int, dict] = {}
        compteur = [0]

        def _indexer(n: NoeudTerme) -> int:
            id_ = compteur[0]
            compteur[0] += 1
            if n.etiquette == ETIQUETTE_VAR:
                noeuds[id_] = {"nom": n.nom, "type": ETIQUETTE_VAR,
                                "arite": 0, "enfants": []}
            elif n.etiquette == ETIQUETTE_CONS:
                noeuds[id_] = {"nom": n.nom, "type": ETIQUETTE_CONS,
                                "arite": 0, "enfants": []}
            else:
                enfants_ids: list = []
                noeuds[id_] = {"nom": n.nom, "type": TYPE_FONC,
                                "arite": int(n.etiquette), "enfants": enfants_ids}
                for enfant in n.enfants:
                    enfants_ids.append(_indexer(enfant))
            return id_

        racine = _indexer(noeud)
        return TermeDict(noeuds, racine, compteur[0])

    @staticmethod
    def depuis_litteral(lit: Litteral) -> "TermeDict":
        """
        Construit un TermeDict depuis un Litteral.
        Le prédicat devient le noeud racine (TYPE_PRED, id=0),
        les termes du littéral sont les enfants.

        Ex : P(f(X), a) →
            {0: P(pred), 1: f(fonc), 2: X(var), 3: a(cons)}

        Args:
            lit (Litteral) : littéral
        Returns:
            TermeDict : littéral représenté comme dict plat
        """
        noeuds: Dict[int, dict] = {}
        compteur = [0]

        # Id 0 : prédicat racine
        id_pred = compteur[0]
        compteur[0] += 1
        enfants_ids: list = []
        noeuds[id_pred] = {"nom": lit.predicat, "type": TYPE_PRED,
                            "arite": lit.arity, "enfants": enfants_ids}

        def _indexer(n: NoeudTerme) -> int:
            id_ = compteur[0]
            compteur[0] += 1
            if n.etiquette == ETIQUETTE_VAR:
                noeuds[id_] = {"nom": n.nom, "type": ETIQUETTE_VAR,
                                "arite": 0, "enfants": []}
            elif n.etiquette == ETIQUETTE_CONS:
                noeuds[id_] = {"nom": n.nom, "type": ETIQUETTE_CONS,
                                "arite": 0, "enfants": []}
            else:
                enfants_ids_fonc: list = []
                noeuds[id_] = {"nom": n.nom, "type": TYPE_FONC,
                                "arite": int(n.etiquette),
                                "enfants": enfants_ids_fonc}
                for enfant in n.enfants:
                    enfants_ids_fonc.append(_indexer(enfant))
            return id_

        for terme in lit.enfants:
            enfants_ids.append(_indexer(terme))

        return TermeDict(noeuds, id_pred, compteur[0])

    # Affichage et comparaison

    def __eq__(self, autre: object) -> bool:
        if not isinstance(autre, TermeDict):
            return False
        return repr(self) == repr(autre)

    def __repr__(self) -> str:
        noeud = self._noeuds[self._racine]
        if noeud["type"] in [ETIQUETTE_VAR, ETIQUETTE_CONS]:
            return noeud["nom"]
        enfants_str = ", ".join(
            TermeDict(self._noeuds, e, self._compteur).__repr__()
            for e in noeud["enfants"]
        )
        return f"{noeud['nom']}({enfants_str})"