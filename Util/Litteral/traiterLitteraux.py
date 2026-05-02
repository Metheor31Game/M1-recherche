from Util.TermStore.TermList import TermSystem
from Algos.MartelliMontanari.MartelliMontanari import MartelliMontanari, UnificationError
from Util.Litteral.Litteral import Litteral

def traiter_litteraux(liste_litteraux):

    succes = 0
    echec = 0
    comparaisons = 0

    for i in range(len(liste_litteraux)):
        for j in range(i+1, len(liste_litteraux)):

            l1 = liste_litteraux[i]
            l2 = liste_litteraux[j]

            comparaisons += 1

            if l1.predicat == l2.predicat and l1.sign != l2.sign:
                if l1.arity != l2.arity:
                    #print(f"Échec : Arités différentes pour {l1} et {l2}")
                    echec += 1
                    continue

                system = TermSystem()

                for t1, t2 in zip(l1.enfants, l2.enfants):
                    system.add(t1, t2)

                mm = MartelliMontanari(system)

                try:
                    unificateur=mm.solve()
                    #print("Unification réussie")
                    succes += 1

                    if unificateur.is_empty():
                     #print("   (Système vide : les termes étaient identiques)")
                     pass
                    else:
                        for eq in unificateur.equations:
                            #print(f"   {eq.left} --> {eq.right}")
                            pass
                except UnificationError:
                    #print("Échec") 
                    echec += 1
    print("Fin du traitement.")
    return comparaisons, succes, echec


def lit_liste(l1: Litteral, list_litteraux: list[Litteral], touteUnif=True):
    resultat = {}
    for l2 in list_litteraux: # Etape 1 : On compare le littéral l1 avec tous les autres littéraux de la liste
        if l1.predicat == l2.predicat and l1.sign != l2.sign and l1.arity == l2.arity: #Etape 2 : On vérifie si les deux prédicats ont les mêmes symboles, les signes opposés et les arités égales
            system = TermSystem() 

            for t1, t2 in zip(l1.enfants, l2.enfants):
                system.add(t1, t2) # Etape 3 : Si les conditions sont remplies, on crée un système d'équations à partir des enfants des deux littéraux

            mm = MartelliMontanari(system) # Etape 4 : On utilise l'algorithme de Martelli-Montanari pour tenter de résoudre le système d'équations
            try:
                unificateur=mm.solve()                  
                resultat[l2] = unificateur
                if not touteUnif:
                    return resultat # Ici on retourne dès la première unification réussie
            except UnificationError:
                pass
    return resultat