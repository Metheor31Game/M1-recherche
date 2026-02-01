import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from Util.TermStore.terme import FabriqueDeTermes, GenerateurDeTermesAleatoires
from Util.TermStore.ListStore import ListStore
from Util.TermStore.SetStore import SetStore
from robinson import unify, afficher, afficherAll, afficherMax

generateur: GenerateurDeTermesAleatoires = GenerateurDeTermesAleatoires(2,2)



def benchmark(n):
    print(f"\n{'='*50}")
    print(f"Benchmark avec {n} termes")
    print(f"{'='*50}")
    
    # Génération des termes
    start_gen = time.time()
    tn1 = SetStore()
    tn2 = ListStore()
    while len(tn1) < n + 1:
        t = generateur.generer_terme_aleatoire()
        tn1.push(t)
        tn2.push(t)
    end_gen = time.time()
    print(f"Temps de génération : {end_gen - start_gen:.4f}s")

    for t in [tn1,tn2]:
        t1 = t.pop()
        
        # Unification
        start_unif = time.time()
        afficherMax(t1, t, type(t)())
        end_unif = time.time()
        print(f"Temps d'unification avec {type(t)()}: {end_unif - start_unif:.4f}s")
        
        print(f"Temps total avec {type(t)()}: {end_unif - start_gen:.4f}s")


if __name__ == "__main__":
    benchmark(1000000)
    

