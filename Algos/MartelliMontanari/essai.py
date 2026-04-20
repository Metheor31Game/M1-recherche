from Util.Litteral.Litteral import Litteral
from Util.TermStore.TermList import TermSystem
from Algos.MartelliMontanari.MartelliMontanari import MartelliMontanari, UnificationError

if __name__ == "__main__":

    litteraux = [
        Litteral.from_string("¬P(f(Y), g(Z), X)"),
        Litteral.from_string("P(Y, g(X), X)"),
        Litteral.from_string("P(X, a, Z)"),
        Litteral.from_string("P(f(a), X, X)"),
        Litteral.from_string("P(X, g(a), X)"),
        Litteral.from_string("P(X, g(f(Y)), X)"),
        Litteral.from_string("P(f(Y), g(a), X)"),
        Litteral.from_string("P(f(Z), g(Z), Z)"),
        Litteral.from_string("P(f(a), g(Z), a)"),
        Litteral.from_string("P(f(g(a)), g(Z), X)"),
    ]

    print("=== Test unification : ¬P(f(Y), g(Z), X) contre la liste ===\n")

    for i in range(len(litteraux)):
        for j in range(i + 1, len(litteraux)):
            l1 = litteraux[i]
            l2 = litteraux[j]

            if l1.predicat == l2.predicat and l1.sign != l2.sign and l1.arity == l2.arity:

                print(f"Couple : {l1}  ⟺  {l2}")

                system = TermSystem()
                for t1, t2 in zip(l1.enfants, l2.enfants):
                    system.add(t1, t2)

                mm = MartelliMontanari(system)
                try:
                    unificateur = mm.solve()
                    if unificateur.is_empty():
                        print("  → Succès (termes identiques, système vide)\n")
                    else:
                        print("  → Succès, unificateur :")
                        for eq in unificateur.equations:
                            print(f"      {eq.left} = {eq.right}")
                        print()
                except UnificationError as e:
                    print(f"  → Échec : {e}\n")