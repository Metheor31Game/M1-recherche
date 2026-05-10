from unification.utils.serialisation import serialiser, deserialiser
from unification.robinson import unifLitteraux, unifyAll, rechercherUnifiablesSimple
from unification.utils.stores import ListStore
from unification.utils.logique.litteral import Litteral, GenerateurLitteralAleatoire


def test1():
    predString = "P(f(X,a),Y).¬P(f(Y,Z),c)"

    listPredicatStr = [pred.strip() for pred in predString.split(".") if pred.strip()]
    listPredicat = [Litteral.from_string(pred) for pred in listPredicatStr]

    print(listPredicat)

    result = unifLitteraux(listPredicat[0], listPredicat[1])

    print(result)

def test2():
    # Teste la serialisation et l'unification en meme temps, pour vérifier que tout va bien

    gen = GenerateurLitteralAleatoire(["P", "Q", "R"], 2, 2)
    listPred = gen.generer_litteraux(30)

    serialiser(listPred, "testPred")

    listPred2 = deserialiser("testPred")

    # remplir le store
    store = ListStore()
    for e in listPred2:
        store.push(e)

    pred1 = store.pop()

    print("Unification avec", pred1)
    print(rechercherUnifiablesSimple(pred1, store))
    
def test3():
    # teste le prétraitement de robinson
    gen = GenerateurLitteralAleatoire(["P", "Q", "R"], 2, 2)
    listPred = gen.generer_litteraux(30)

    store = ListStore()
    for e in listPred:
        store.push(e)

    candidat = store.pop()

    print("Candidat : \n")
    print(candidat)

    print("\nAvant prétraitement : \n")
    print(store)

    #prétraitement
    store.pretraitement(candidat)
    print("\nAprès prétraitement : \n")
    print(store)

#test1()
#test2()
# test3()

print(Litteral.from_string("R(b, g(a, Y, U), b, f(a, V), U, l(b, Y), a, g(e, Y, b), f(a, c))").afficher_arbre())


