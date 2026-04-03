from Util.Litteral.Litteral import Litteral
from Util.TermStore.StructureMM.TermeArbre import TermeArbre
from Util.TermStore.StructureMM.TermeDict import TermeDict
from Util.TermStore.StructureMM.TermeAbstrait import TermeAbstrait
from Util.TermStore.TermList import TermSystem
from Algos.MM.MartelliMontanari import MartelliMontanari, UnificationError
from Algos.MM.traiterLitterauxList import traiter_litteraux
from Algos.MM.traiterLitterauxDictionnaire import traiter_litteraux_dict


# ── Helpers ───────────────────────────────────────────────────────────────────

def _unifier(l1: Litteral, l2: Litteral, structure: str) -> str:
    """
    Tente d'unifier deux littéraux avec la structure choisie.

    Args:
        l1        (Litteral) : premier littéral
        l2        (Litteral) : second littéral
        structure (str)      : "arbre" ou "dict"
    Returns:
        str : résultat lisible (substitution ou message d'erreur)
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

    mm = MartelliMontanari(system)

    try:
        resultat = mm.solve()
        if resultat.is_empty():
            return "substitution vide (termes identiques)"
        substitutions = [f"{eq.left} → {eq.right}" for eq in resultat.equations]
        return "{ " + ", ".join(substitutions) + " }"
    except UnificationError as e:
        return f"Échec — {e}"


def tester(nom: str, lit_pos: str, lit_neg: str, attendu: str):
    """
    Teste l'unification de deux littéraux avec TermeArbre et TermeDict.

    Args:
        nom     (str) : nom du test
        lit_pos (str) : littéral positif  ex: "P(f(X), a)"
        lit_neg (str) : littéral négatif  ex: "¬P(f(b), Y)"
        attendu (str) : résultat attendu  ex: "succes" ou "echec"
    """
    print(f"{'─' * 55}")
    print(f"Test     : {nom}")
    print(f"Littéraux: {lit_pos}  vs  {lit_neg}")
    print(f"Attendu  : {attendu}")
    print()

    l1 = Litteral.from_string(lit_pos)
    l2 = Litteral.from_string(lit_neg)

    res_arbre = _unifier(l1, l2, "arbre")
    res_dict  = _unifier(l1, l2, "dict")

    print(f"  TermeArbre → {res_arbre}")
    print(f"  TermeDict  → {res_dict}")

    # Vérification cohérence entre les deux structures
    coherent = (("Échec" in res_arbre) == ("Échec" in res_dict))
    print(f"  {'✅ Cohérent' if coherent else '❌ INCOHÉRENCE entre les deux structures'}")
    print()


# ══════════════════════════════════════════════════════
# SECTION 1 — Tests unitaires
# ══════════════════════════════════════════════════════

def section_tests_unitaires():
    print("=" * 55)
    print("SECTION 1 — Tests unitaires")
    print("=" * 55)
    print()

    # Cas 1 : unification simple
    # P(f(X), a) vs ¬P(f(b), Y)
    # DECOMPOSE → f(X)=f(b) et a=Y
    # DECOMPOSE → X=b | ORIENT → Y=a
    # Attendu   → {X→b, Y→a}
    tester(
        "Unification simple",
        "P(f(X), a)",
        "¬P(f(b), Y)",
        "succès : {X→b, Y→a}"
    )

    # Cas 2 : clash fonctions
    # P(f(X)) vs ¬P(g(X))
    # DECOMPOSE → f(X)=g(X) → CLASH
    # Attendu   → échec
    tester(
        "Clash — fonctions différentes",
        "P(f(X))",
        "¬P(g(X))",
        "échec (CLASH f≠g)"
    )

    # Cas 3 : clash constantes
    # P(a) vs ¬P(b)
    # DECOMPOSE → a=b → CLASH
    # Attendu   → échec
    tester(
        "Clash — constantes différentes",
        "P(a)",
        "¬P(b)",
        "échec (CLASH a≠b)"
    )

    # Cas 4 : occur check
    # P(X) vs ¬P(f(X))
    # DECOMPOSE → X=f(X) → OCCUR CHECK
    # Attendu   → échec
    tester(
        "Occur check",
        "P(X)",
        "¬P(f(X))",
        "échec (OCCUR CHECK)"
    )

    # Cas 5 : termes identiques
    # P(a, b) vs ¬P(a, b)
    # DECOMPOSE → a=a et b=b → DELETE les deux
    # Attendu   → substitution vide
    tester(
        "Termes identiques",
        "P(a, b)",
        "¬P(a, b)",
        "substitution vide"
    )

    # Cas 6 : variable partagée en conflit
    # P(X, X) vs ¬P(a, b)
    # DECOMPOSE → X=a et X=b
    # SUBSTITUTE X→a dans X=b → a=b → CLASH
    # Attendu   → échec
    tester(
        "Variable partagée — conflit",
        "P(X, X)",
        "¬P(a, b)",
        "échec (conflit sur X)"
    )

    # Cas 7 : unification imbriquée
    # P(f(X, g(Y))) vs ¬P(f(a, g(b)))
    # DECOMPOSE → f(X,g(Y))=f(a,g(b))
    # DECOMPOSE → X=a et g(Y)=g(b)
    # DECOMPOSE → Y=b
    # Attendu   → {X→a, Y→b}
    tester(
        "Unification imbriquée",
        "P(f(X, g(Y)))",
        "¬P(f(a, g(b)))",
        "succès : {X→a, Y→b}"
    )


# ══════════════════════════════════════════════════════
# SECTION 2 — Tests sur liste de littéraux
# ══════════════════════════════════════════════════════

def section_tests_liste():
    print("=" * 55)
    print("SECTION 2 — Tests sur liste de littéraux")
    print("=" * 55)
    print()

    # Liste concrète de littéraux dont on connaît les paires
    # complémentaires possibles :
    #
    #   P(f(X), a)   et ¬P(f(b), Y)  → succès  {X→b, Y→a}
    #   P(a, b)      et ¬P(a, b)      → succès  substitution vide
    #   Q(X)         et ¬Q(f(X))      → échec   occur check
    #   Q(a)         et ¬Q(b)         → échec   clash
    #   R(f(X), g(Y)) et ¬R(f(a), g(b)) → succès {X→a, Y→b}

    liste_litteraux = [
        Litteral.from_string("P(f(X), a)"),
        Litteral.from_string("¬P(f(b), Y)"),
        Litteral.from_string("P(a, b)"),
        Litteral.from_string("¬P(a, b)"),
        Litteral.from_string("Q(X)"),
        Litteral.from_string("¬Q(f(X))"),
        Litteral.from_string("Q(a)"),
        Litteral.from_string("¬Q(b)"),
        Litteral.from_string("R(f(X), g(Y))"),
        Litteral.from_string("¬R(f(a), g(b))"),
    ]

    print("Liste des littéraux :")
    for i, lit in enumerate(liste_litteraux):
        print(f"  [{i}] {lit}")
    print()

    # ── traiter_litteraux (naïf) ──────────────────────────────────────────
    print("─" * 55)
    print("traiter_litteraux — naïf O(n²)")
    print("─" * 55)

    print("  Avec TermeArbre :")
    comp, succ, ech = traiter_litteraux(liste_litteraux, structure="arbre")
    print(f"    comparaisons={comp}, succès={succ}, échecs={ech}")
    print()

    print("  Avec TermeDict :")
    comp, succ, ech = traiter_litteraux(liste_litteraux, structure="dict")
    print(f"    comparaisons={comp}, succès={succ}, échecs={ech}")
    print()

    # ── traiter_litteraux_dict (index prédicat+signe) ─────────────────────
    print("─" * 55)
    print("traiter_litteraux_dict — index prédicat+signe")
    print("─" * 55)

    print("  Avec TermeArbre :")
    comp, succ, ech = traiter_litteraux_dict(liste_litteraux, structure="arbre")
    print(f"    comparaisons={comp}, succès={succ}, échecs={ech}")
    print()

    print("  Avec TermeDict :")
    comp, succ, ech = traiter_litteraux_dict(liste_litteraux, structure="dict")
    print(f"    comparaisons={comp}, succès={succ}, échecs={ech}")
    print()


# ══════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════

if __name__ == "__main__":
    section_tests_unitaires()
    section_tests_liste()