import time

from unification.utils.logique.litteral import GenerateurLitteralAleatoire
from unification.martelli_montanari import traiterLitterauxSet, traiterLitterauxDict, traiterLitteraux

# On génère une liste de 10000 littéraux aléatoires
generateur = GenerateurLitteralAleatoire(['P', 'Q', 'R','S'], ariteMax=3, profondeurMax=3)
liste_litteraux = generateur.generer_litteraux(10000)


print(f"Benchmark pour 10000 littéraux")

debut = time.perf_counter()
comp, succ, ech = traiterLitteraux(liste_litteraux)
fin   = time.perf_counter()
 
print("--- Liste ---")
print(f"  Comparaisons : {comp}")
print(f"  Succès       : {succ}")
print(f"  Échecs       : {ech}")
print(f"  Temps        : {fin - debut} s")
print()
 
# dictionnaire 
debut = time.perf_counter()
comp, succ, ech = traiterLitterauxDict(liste_litteraux)
fin   = time.perf_counter()
 
print("--- Dictionnaire  ---")
print(f"  Comparaisons : {comp}")
print(f"  Succès       : {succ}")
print(f"  Échecs       : {ech}")
print(f"  Temps        :  {fin - debut} s")
print()
 
#   Set
debut = time.perf_counter()
comp, succ, ech = traiterLitterauxSet(liste_litteraux)
fin   = time.perf_counter()
 
print("--- Set ---")
print(f"  Comparaisons : {comp}")
print(f"  Succès       : {succ}")
print(f"  Échecs       : {ech}")
print(f"  Temps        : {fin - debut} s")
print()