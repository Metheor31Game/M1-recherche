import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from Util.TermStore.terme import FabriqueDeTermes
from Util.TermStore.ListStore import ListStore
from Util.TermStore.SetStore import SetStore
from Util.Litteral.Litteral import Litteral, GenerateurLitteralAleatoire

from Util.Serialisation.serialisation import serialiser, deserialiser

from Algos.Predicat.unifPredicat import unifPredicat, unifyAll, rechercherUnifiablesSimple

def test1():
    predString = "P(f(X,a),Y).¬P(f(Y,Z),c)"

    listPredicatStr = [pred.strip() for pred in predString.split(".") if pred.strip()]
    listPredicat = [Litteral.from_string(pred) for pred in listPredicatStr]

    print(listPredicat)

    result = unifPredicat(listPredicat[0], listPredicat[1], "Robinson")

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
    print(rechercherUnifiablesSimple(pred1, store, "Robinson"))
    

#test1()
test2()



