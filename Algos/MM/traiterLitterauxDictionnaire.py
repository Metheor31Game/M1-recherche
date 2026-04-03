from Util.TermStore.TermList import TermSystem
from Util.TermStore.StructureMM.TermeArbre import TermeArbre
from Util.TermStore.StructureMM.TermeDict import TermeDict
from Algos.MM.MartelliMontanari import MartelliMontanari, UnificationError


def indexer_par_predicat(liste_litteraux) -> dict:
    """
    Construit un index des littéraux groupés par prédicat et par signe.

    Structure de l'index :
        {
            "P": {
                "positifs": [P(f(X)), P(a), ...],
                "negatifs": [¬P(b), ...]
            },
            "Q": {
                "positifs": [...],
                "negatifs": [...]
            }
        }

    Avantage par rapport à un index simple par prédicat :
        On ne compare QUE positifs vs négatifs — les comparaisons
        entre deux littéraux de même signe sont évitées dès l'indexation,
        sans avoir à vérifier le signe dans la boucle de comparaison.

    Args:
        liste_litteraux (List[Litteral]) : liste des littéraux
    Returns:
        dict : index {prédicat → {positifs, négatifs}}
    """
    index = {}

    for lit in liste_litteraux:
        if lit.predicat not in index:
            index[lit.predicat] = {"positifs": [], "negatifs": []}

        if lit.sign:
            index[lit.predicat]["positifs"].append(lit)
        else:
            index[lit.predicat]["negatifs"].append(lit)

    return index


def _construire_system(l1, l2, structure: str) -> TermSystem:
    """
    Construit un TermSystem à partir de deux littéraux en choisissant
    la structure de données utilisée pour représenter les termes.

    Chaque littéral est converti en un seul terme dont la racine est
    le prédicat — ex : P(f(X), a) devient un terme avec P comme racine.

    Args:
        l1        (Litteral) : littéral positif
        l2        (Litteral) : littéral négatif
        structure (str)      : "arbre", "dict" ou "liste"
    Returns:
        TermSystem : système prêt pour MM
    """
    system = TermSystem()

    if structure == "arbre":
        system.add(
            TermeArbre.depuis_litteral(l1),
            TermeArbre.depuis_litteral(l2)
        )
    elif structure == "dict":
        system.add(
            TermeDict.depuis_litteral(l1),
            TermeDict.depuis_litteral(l2)
        )
    else:
        raise ValueError(
            f"Structure inconnue : {structure}. Choisir 'arbre', 'dict' ou 'liste'."
        )

    return system


def traiter_litteraux_dict(liste_litteraux, structure: str = "arbre"):
    """
    Args:
        liste_litteraux (List[Litteral]) : liste des littéraux à traiter
        structure       (str)            : structure de données pour MM
                                          "arbre" | "dict" | "liste"
    Returns:
        tuple : (comparaisons, succes, echec)
    """
    succes       = 0
    echec        = 0
    comparaisons = 0

    index = indexer_par_predicat(liste_litteraux)

    for predicat, groupe in index.items():
        positifs = groupe["positifs"]
        negatifs = groupe["negatifs"]

        for l1 in positifs:
            for l2 in negatifs:

                comparaisons += 1

                if l1.arity != l2.arity:
                    echec += 1
                    continue

                system = _construire_system(l1, l2, structure)
                mm     = MartelliMontanari(system)

                try:
                    mm.solve()
                    succes += 1
                except UnificationError:
                    echec += 1

    print(f"[traiter_litteraux_dict | {structure}] "
          f"comparaisons={comparaisons}, succes={succes}, echec={echec}")
    return comparaisons, succes, echec
