from Util.TermStore.terme import FabriqueDeTermes, NoeudTerme
from Util.TermStore.TermList import TermSystem
from Algos.MartelliMontanari import UnificationError, MartelliMontanari

def run_test(name, system):
    print(f"\n--- {name} ---")
    algo = MartelliMontanari(system)
    try:
        result = algo.solve()
        print(f"RÉSULTAT : {result}")
    except UnificationError as e:   
        print(f"ÉCHEC : {e}")


# f(X, a) = f(b, Y)  =>  Solution : {X=b, Y=a}
test_1 = TermSystem()
test_1.add(
    FabriqueDeTermes.creer_fonc("f", 2, [FabriqueDeTermes.creer_var("X"), FabriqueDeTermes.creer_cons("a")]),
    FabriqueDeTermes.creer_fonc("f", 2, [FabriqueDeTermes.creer_cons("b"), FabriqueDeTermes.creer_var("Y")])
)

# f(X) = g(X)
test_2 = TermSystem()
test_2.add(
    FabriqueDeTermes.creer_fonc("f", 1, [FabriqueDeTermes.creer_var("X")]),
    FabriqueDeTermes.creer_fonc("g", 1, [FabriqueDeTermes.creer_var("X")])
)

# X = f(X) 
test_3 = TermSystem()
x_var = FabriqueDeTermes.creer_var("X")
test_3.add(
    x_var,
    FabriqueDeTermes.creer_fonc("f", 1, [x_var])
)

# { X = Y, Y = a } => Solution : { X=a, Y=a }
test_4 = TermSystem()
test_4.add(FabriqueDeTermes.creer_var("X"), FabriqueDeTermes.creer_var("Y"))
test_4.add(FabriqueDeTermes.creer_var("Y"), FabriqueDeTermes.creer_cons("a"))

# f(X, X, Y) = f(f(Y, Y, Z), f(Y, X, Z), a)
test_5 = TermSystem()

# f(X, X, Y)
x_var = FabriqueDeTermes.creer_var("X")
y_var = FabriqueDeTermes.creer_var("Y")
z_var = FabriqueDeTermes.creer_var("Z")
a_const = FabriqueDeTermes.creer_cons("a")

term_left = FabriqueDeTermes.creer_fonc("f", 3, [x_var, x_var, y_var])

# f(f(Y, Y, Z), f(Y, X, Z), a)
inner_f1 = FabriqueDeTermes.creer_fonc("f", 3, [y_var, y_var, z_var])
inner_f2 = FabriqueDeTermes.creer_fonc("f", 3, [y_var, x_var, z_var])
term_right = FabriqueDeTermes.creer_fonc("f", 3, [inner_f1, inner_f2, a_const])

test_5.add(term_left, term_right)

#f(X, X) = f(g(Y), Y)
test_6 = TermSystem()

x_var = FabriqueDeTermes.creer_var("X")
y_var = FabriqueDeTermes.creer_var("Y")
g_func = FabriqueDeTermes.creer_fonc("g", 1, [y_var])

# f(X, X)
term_left = FabriqueDeTermes.creer_fonc("f", 2, [x_var, x_var])
# f(g(Y), Y)
term_right = FabriqueDeTermes.creer_fonc("f", 2, [g_func, y_var])

test_6.add(term_left, term_right)


if __name__ == "__main__":
    run_test("test_1", test_1)
    run_test("test_2", test_2)
    run_test("test_3", test_3)
    run_test("test_4", test_4)
    run_test('test_5', test_5)
    run_test('test_6', test_6)