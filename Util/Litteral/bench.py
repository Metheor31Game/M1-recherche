from typing import Optional, List
import time
import random
from Util.TermStore.terme import GenerateurDeTermesAleatoires
from Util.Litteral.Litteral import Litteral
from Util.Litteral.traiterLitteraux import traiter_litteraux


#aidé par l'IA
def generer_litteraux_aleatoires(n: int, generateur: GenerateurDeTermesAleatoires) -> List[Litteral]:
    litteraux = []
    predicats = ["P", "Q", "R"]
    
    for _ in range(n):
        nom_p = random.choice(predicats)
        nb_arguments = 2 
        arguments = [generateur.generer_terme_aleatoire() for _ in range(nb_arguments)]
        signe = random.choice([True, False])
        
        litteraux.append(Litteral(nom_p, arguments, signe))
    return litteraux

def benchmark_aleatoire(nb_litteraux: int, profondeur: int):
    print(f"\n LANCEMENT DU BENCHMARK ALÉATOIRE")
    print(f"Configuration : {nb_litteraux} littéraux, Profondeur max des termes : {profondeur}")
    print("-" * 50)

    # Initialisation du générateur
    gen = GenerateurDeTermesAleatoires(profondeur_max=profondeur)
    
    # Génération de la liste de test
    clause_test = generer_litteraux_aleatoires(nb_litteraux, gen)
    
    # Mesure du temps de traitement
    start = time.perf_counter()
    traiter_litteraux(clause_test)
    end = time.perf_counter()
    
    print("-" * 50)
    print(f" Benchmark terminé en {(end - start) * 1000:.4f} ms")

if __name__ == "__main__":
    # Test avec 20 littéraux aléatoires et une profondeur de 3
    benchmark_aleatoire(nb_litteraux=20, profondeur=3)