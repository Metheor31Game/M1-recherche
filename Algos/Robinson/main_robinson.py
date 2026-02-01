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
    
    # Génération des termes dans une liste d'abord
    start_gen = time.time()
    termes_generes = []
    while len(termes_generes) < n + 1:
        termes_generes.append(generateur.generer_terme_aleatoire())
    end_gen = time.time()
    print(f"Temps de génération : {end_gen - start_gen:.4f}s")
    
    # Récupération de t1
    t1 = termes_generes[0]
    termes_a_unifier = termes_generes[1:]

    # On doit refaire les store car sinon t1 serait différent
    for StoreClass in [SetStore, ListStore]:
        # Recréer le store avec les mêmes termes pour chaque test
        store = StoreClass()
        for t in termes_a_unifier:
            store.push(t)
        
        # Unification
        start_unif = time.time()
        afficherMax(t1, store, StoreClass())
        end_unif = time.time()
        print(f"Temps d'unification avec {StoreClass.__name__}: {end_unif - start_unif:.4f}s")
        
        print(f"Temps total avec {StoreClass.__name__}: {end_unif - start_gen:.4f}s\n")


if __name__ == "__main__":
    benchmark(1000000)
    

