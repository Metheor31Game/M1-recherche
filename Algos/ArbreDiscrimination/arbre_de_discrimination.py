import sys
import os

racine_projet = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.append(os.path.abspath(racine_projet))

from Util.TermStore.terme import NoeudTerme, ETIQUETTE_CONS, ETIQUETTE_VAR
from typing import List, Dict, Any, Optional, Tuple, NamedTuple


# TODO REVOIR ENTIERETE POUR GESTION ERREUR ?

# Normalisation différente selon si var dans l'arbre ou dans le terme recherché 
NORM_VAR_ARBRE = "*"    # Exemple :  f(X, Y) -> ['f', '*1', '*2']
NORM_VAR_REQUETE = "?"  # Exemple :  f(X, Y) -> ['f', '?1', '?2']


class ResultatRecherche(NamedTuple):
    """
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║       Format de résultat proposé par IA (ClaudeCode).          ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    Résultat d'une recherche de termes unifiables dans l'arbre de discrimination.

    Attributes:
        substitution    (Dict[str, List[str]])  :   Substitution associant les noms des varibales originaux
                                                    du terme de recherche à leur séquence de symboles en notation préfixe.
        pointeurs       (List[Any])             :   Pointeurs associés au terme unifiable trouvé dans l'arbre    

    """
    substitution: Dict[str, List[str]]
    pointeurs: List[Any]

class NoeudArbreDeDiscrimination:
    """
    Classe d'un noeud dans l'arbre de discrimination.

    Attributes:
        symbole     (Optional[str])                             :   Symbole représentant le noeud (ex : X, f, a, etc.). 
                                                                    'None' pour le noeud racine.
        enfants     (Dict[str, 'NoeudArbreDeDiscrimination'])   :   Noeuds enfants, indexés par leur symbole.
        pointeurs   (List[Any])                                 :   Pointeurs vers les termes associés à ce noeud.
    """
    def __init__(self, symbole: Optional[str] = None) -> None:
        self.symbole = symbole # Symbole du noeud (None pour la racine)
        self.enfants = {} # Noeuds enfants
        self.pointeurs = [] # Pointeurs vers les termes associés à ce noeud


class ArbreDeDiscrimination:
    """
    Arbre de discrimination pour stocker des termes. 
    Permet la recherche de termes unifiables.

    Les termes sont représentés en notation préfixe aplatie.
    
    Chaque chemin racine -> feuille encore un terme.
    
    Attributes:
        racine ('NoeudArbreDeDiscrimination')   :   Noeud racine de l'arbre. 'None' par défaut
        arites (Dict[str, int])                 :   Dictionnaire pour stocker l'arité de chaque symbole dans l'arbre
        taille (int)                            :   Taille de l'arbre  
    """
    
    def __init__(self) -> None:
        self.racine = NoeudArbreDeDiscrimination()
        self.arites = {} # Stocker les arités de tous les symboles
        self.taille = 0 # Stock la taille

    def _mapper_arite(self, terme: NoeudTerme) -> None:
        """
        Récupère les arités de l'ensemble des symboles du terme donné
        et les ajoutes au dictionnaire des arités de la structure.

        Args:
            terme (NoeudTerme)  :   Le terme a traiter
        """
        # Pour constante et variable :
        if terme.etiquette in (ETIQUETTE_CONS, ETIQUETTE_VAR):
            if terme.nom not in self.arites:
                self.arites[terme.nom] = 0 # On met à 0
        # Pour fonction :
        else: 
            if terme.nom not in self.arites:
                self.arites[terme.nom] = terme.etiquette # L'arité est stockée dans l'étiquette
            # Recherche dans les arguments de la fonction :
            for sous_terme in terme.enfants:
                self._mapper_arite(sous_terme)

    def inserer(self, terme: NoeudTerme, pointeur: Any) -> None:
        """
        Insère un terme dans l'arbre de discrimination avec un pointeur associé.

        Le terme est parcouru en ordre préfixe pour créer un seul chemin dans l'arbre.
        Par exemple, f(X, g(Y)) crée le chemin : f -> *1 -> g -> *2

        Args:
            terme       (NoeudTerme)    :   Le terme à insérer dans l'arbre.
            pointeur    (Any)           :    Un pointeur à associer avec ce terme.
        """

        # On ajoute au dictionnaire des arités les arités des nouveaux symboles :
        self._mapper_arite(terme)

        # Mise à plat du terme en une séquence de symboles issue d'un parcours préfixe
        # On normalise aussi les variables :
        var_map = {}
        sequence = self._mise_a_plat(terme, var_map, NORM_VAR_ARBRE)
        
        # Insertion dans l'arbre :
        noeud_courant = self.racine
        for symbole in sequence:
            if symbole not in noeud_courant.enfants:
                noeud_courant.enfants[symbole] = NoeudArbreDeDiscrimination(symbole)
            noeud_courant = noeud_courant.enfants[symbole]
        
        # Ajout du pointeur au noeud feuille :
        if pointeur not in noeud_courant.pointeurs:
            noeud_courant.pointeurs.append(pointeur)
            self.taille += 1

    def _mise_a_plat(self, terme: NoeudTerme, var_map: Dict[str, str], prefixe: str) -> List[str]:
        """
        Mise à plat d'un terme en une séquence de symboles en ordre préfixe.
        Les variables sont normalisées en *1, *2, etc.
        
        Pour f(X, g(Y)), retourne : ['f', '*1', 'g', '*2']
        
        Args:
            terme   (NoeudTerme)        :   Le terme à aplatir.
            var_map (Dict[str, str])    :   Mapping de normalisation des variables.
            prefixe (str)               :   Préfixe pour les variables normalisées.
        Returns:
            List[str]                   :   Séquence aplatie de symboles.
        """
        # Initialisation de la séquence résultat vide :
        resultat = []
        
        # Ajout du symbole du terme courant :
        if terme.etiquette == ETIQUETTE_VAR:
            # Si c'est une variable, on la normalise :
            if terme.nom not in var_map: # Nouvelle variable rencontrée
                var_map[terme.nom] = f"{prefixe}{len(var_map) + 1}"
            resultat.append(var_map[terme.nom])
        else:
            # Constante ou fonction, on ajoute le nom tel quel :
            resultat.append(terme.nom)
        
            # Ajout des enfants :
            if terme.etiquette not in (ETIQUETTE_CONS, ETIQUETTE_VAR):
                for enfant in terme.enfants:
                    resultat.extend(self._mise_a_plat(enfant, var_map, prefixe))
        
        return resultat
    
    def rechercher_terme(self, terme: NoeudTerme) -> List[ResultatRecherche]:
        """
        Recherche les termes unifiables avec le terme donné dans l'arbre de discrimination.
        
        Pour chaque terme unifiable, on retourne la substitution ainsi que le pointeur associé.
        Ainsi on sait comment instancier les variables afin de réaliser l'unification.

        Args:
            terme (NoeudTerme)      :   Le terme à rechercher.
        Returns:
            List[ResultatRecherche] :   Liste des résultats (comprenant donc pointeur et substitution)
        """
        # On ajoute les symboles du terme recherché au dictionnaire :
        self._mapper_arite(terme)

        # Mise à plat du terme recherché :
        var_map = {}
        terme_mis_a_plat = self._mise_a_plat(terme, var_map, NORM_VAR_REQUETE)
        
        inverse_var_map = {v: k for k, v in var_map.items()}

        resultats_internes = []
        self._recherche_recursive(self.racine, terme_mis_a_plat, 0, {}, resultats_internes)

        resultats = []
        for substitution_norm, pointeurs in resultats_internes:
            substitution = {
                inverse_var_map.get(var_norm, var_norm): seq
                for var_norm, seq in substitution_norm.items()
            }
            resultats.append(ResultatRecherche(substitution=substitution, pointeurs=pointeurs))

        return resultats
        

    
    def _recherche_recursive(self, noeud: NoeudArbreDeDiscrimination, sequence: List[str], index: int, substitution: Dict[str, str], resultats: List[Tuple[Dict[str, str], List[Any]]], debug: bool = False) -> None:
        """
        Fonction récursive pour rechercher des termes unifiables dans l'arbre de discrimination.

        Args:
            noeud           (NoeudArbreDeDiscrimination)                    : Noeud courant dans l'arbre.
            sequence        (List[str])                                     : Séquence aplatie du terme recherché.
            index           (int)                                           : Index actuel dans la séquence.
            substitution    (Dict[str, str])                                : Dictionnaire des substitutions
            resultats       (List[Tuple[Dict[str, List[str]], List[Any]]])  : Liste accumulant les pointeurs des termes unifiables trouvés.
            debug           (bool)                                          : Booléen pour gestion d'affichage de messages de debug
        """
        # Cas de base : toute la séquence a été parcourue
        if index >= len(sequence):
            if noeud.pointeurs:
                resultats.append((dict(substitution), list(noeud.pointeurs))) # Ajouter les pointeurs du noeud courant
            return
            
        symbole_courant = sequence[index]

        # Recherche dans les enfants du noeud courant
        for enfant in noeud.enfants.values():

            # Cas 1 : le symbole courant est le même que celui du noeud enfant
            if symbole_courant == enfant.symbole:
                # Aucune substitution, on avance
                self._recherche_recursive(enfant, sequence, index + 1, substitution, resultats) # On continue à chercher dans cet enfant
            
            # Cas 2 : le symbole de la recherche est une variable
            elif symbole_courant.startswith(NORM_VAR_REQUETE):
                if debug:
                    print(f"RECHERCHE POUR {symbole_courant} DANS {sequence}:")

                # Récupère les sous-termes de l'arbre pour substitution :
                for sous_terme_seq, dernier_noeud in self._collecter_sous_termes(enfant, 1, []):
                    if debug:
                        print(f"SOUS SEQUENCE : {sous_terme_seq}")

                    # Vérification de l'occur check (symbole de la substitution présent dans sous-terme qu'on substitute) :
                    if symbole_courant in sous_terme_seq:
                        if debug:
                            print("OCCUR CHECK")
                        continue # Abandon de la branche

                    # Si variable est déjà substituée :
                    if symbole_courant in substitution:
                        if debug:
                            print(f"TERME {symbole_courant} DEJA SUBSTITUE")
                        
                        # Si c'est la même substitution déjà enregistrée :
                        if substitution[symbole_courant] == sous_terme_seq:
                            if debug:
                                print(f"MEME SUBSTITUTION, ON CONTINU")

                            # On peut continuer la recherche 
                            self._recherche_recursive(dernier_noeud, sequence, index + 1, substitution, resultats)
                        
                        # Sinon, il faut tester la compatibilité de la substitution :
                        else:
                            if debug:
                                print(f"NOUVELLE SUBSTITUTION, ON CREE UNE TRANSITIVITE")
                            
                            # La variable de la recherche a été substituée à : une fonction, une constante ou une variable 

                            sous_terme = " ".join(sous_terme_seq)

                            # CAS 1 : Variables (commence par *)
                            if substitution[symbole_courant].startswith(NORM_VAR_ARBRE):
                                if debug:
                                    print(f"TERME SUBSTITUE EST UNE VARIABLE, ON L'A SUBSTITUE A SON TOUR")

                                nouvelle_substitution = {**substitution, substitution[symbole_courant]: sous_terme}
                                self._recherche_recursive(dernier_noeud, sequence, index + 1, nouvelle_substitution, resultats)
                            
                            # CAS 2 et 3 : meme comportement puisqu'on ne peut substituer qu'une variable
                            else:
                                if debug:
                                    print(f"TERME SUBSITUTE EST UNE CONSTANTE OU FONCTION")
                                
                                # Si le sous-terme est une variable :
                                if sous_terme.startswith(NORM_VAR_ARBRE):
                                    if debug:
                                        print(f"LE SOUS-TERME EST UNE VARIABLE, ON LA SUBSTITUE AU TERME")

                                    # TODO : vérifier occur check avec symbole de base !!!
                                    
                                    # Substitution valide
                                    nouvelle_substitution = {**substitution, sous_terme: substitution[symbole_courant]}
                                    self._recherche_recursive(dernier_noeud, sequence, index + 1, nouvelle_substitution, resultats)
                                
                                # Sinon non.

                    # Nouvelle substitution :
                    else:
                        if debug:
                            print(f"NOUVELLE SUBSITUTION !")

                        sous_terme = " ".join(sous_terme_seq)
                        nouvelle_substitution = {**substitution, symbole_courant: sous_terme}
                        self._recherche_recursive(dernier_noeud, sequence, index + 1, nouvelle_substitution, resultats)

            # Cas 3 : le symbole de l'enfant est une variable
            #         peut s'unifier avec le sous-terme courant de l'arbre
            elif enfant.symbole.startswith(NORM_VAR_ARBRE):
                profondeur = self._calculer_profondeur_depuis_index(index, sequence)
                sous_terme_seq = sequence[index : index + profondeur]
                nouvel_index = index + profondeur

                if nouvel_index > len(sequence):
                    continue

                # Occur Check
                if enfant.symbole in sous_terme_seq:
                    continue

                # Déjà subsitutuée
                if enfant.symbole in substitution:
                    # Si même substitution
                    if substitution[enfant.symbole] == sous_terme_seq:
                        # On continue
                        self._recherche_recursive(enfant, sequence, nouvel_index, substitution, resultats)
                else:
                    # Nouvelle substitution locale
                    nouvelle_substitution = {**substitution, enfant.symbole: sous_terme_seq}
                    self._recherche_recursive(enfant, sequence, nouvel_index, nouvelle_substitution, resultats)

    def _collecter_sous_termes(self, noeud: NoeudArbreDeDiscrimination, obligations: int, chemin: List[str]) -> List[Tuple[List[str], NoeudArbreDeDiscrimination]]:
        """
        Collecte les paires (séquence_sous_terme, noeud_de_continuation)
        correspondant aux sous-termes complets dont la racine est `noeud``

        Args:
            noeud       (NoeudArbreDeDiscrimination)            :   Noeud courant à explorer.
            obligations (int)                                   :   Sous-termes restants.
            chemin      (List[str])                             :   Séquence de symboles accumulée.

        Returns:
            List[Tuple[List[str], NoeudArbreDeDiscrimination]]  :   Paire
        """
        # Ajout du symbole courant au chemin parcouru :
        chemin = chemin + [noeud.symbole or ""] # Pour éviter erreur de typing
        # TODO A REVOIR POUR CORRECTION ERREUR
        
        # Mise à jour du compteur :
        obligations = obligations -1 + self.arites.get(noeud.symbole, 0)

        # Le sous-terme est complet :
        if obligations == 0:
            return [(chemin, noeud)]
        
        # Pas complet, on ajoute les enfants
        resultats = []
        for enfant in noeud.enfants.values():
            resultats.extend(self._collecter_sous_termes(enfant, obligations, chemin))
        
        return resultats
        
    
    def _calculer_profondeur_depuis_index(self, index: int, sequence: List[str]) -> int:
        """
        Calcule la profondeur du sous-terme commençant à l'index donné.
        
        Args:
            index       (int)       : L'index de départ dans la séquence.
            sequence    (List[str]) : La séquence
        Returns:
            int : Le nombre de symboles formant le sous-terme.
        """
        if index >= len(sequence):
            return 0

        symbole = sequence[index]

        if symbole.startswith(NORM_VAR_ARBRE) or symbole.startswith(NORM_VAR_REQUETE):
            return 1
        
        arite = self.arites.get(symbole, 0)
        # Si arité = 0 (variable ou constante), la profondeur est 1
        if arite == 0:
            return 1
        
        # Si arité > 0 (fonction), on compte 1 + profondeur de chaque argument
        profondeur = 1
        position_courante = index + 1
        
        for _ in range(arite):
            profondeur_arg = self._calculer_profondeur_depuis_index(position_courante, sequence)
            profondeur += profondeur_arg
            position_courante += profondeur_arg
        
        return profondeur
        

    
    def affichage_arbre(self, noeud: Optional[NoeudArbreDeDiscrimination] = None, niveau: int = 0, prefixe: str = "", est_dernier: bool = True, chemin: str = "") -> None:
        """
        ╔════════════════════════════════════════════════════════════════╗
        ║                                                                ║
        ║      Structure de la fonction générée par IA (ClaudeCode).     ║
        ║                                                                ║
        ╚════════════════════════════════════════════════════════════════╝

        Affiche l'arbre de discrimination de manière lisible dans la console.
        
        Args:
            noeud (Optional['NoeudArbreDeDiscrimination']) : Le noeud courant à afficher. 'None' pour commencer à la racine.
            niveau (int) : Niveau actuel dans l'arbre, utilisé pour l'indentation.
            prefixe (str) : Chaîne de préfixe pour formater la structure de l'arbre.
            est_dernier (bool) : Indique si le noeud courant est le dernier enfant de son parent.
            chemin (str) : Le chemin vers le noeud courant.
        """
        if noeud is None:
            # Commencer à la racine
            noeud = self.racine
            print("╔" + "═" * 61 + "╗")
            print("║" + " " * 19 + "ARBRE DE DISCRIMINATION" + " " * 19 + "║")
            print("╚" + "═" * 61 + "╝")
            print("\nRACINE")
            liste_enfants = list(noeud.enfants.values())
            for i, noeud_enfant in enumerate(liste_enfants):
                est_dernier_enfant = (i == len(liste_enfants) - 1)
                self.affichage_arbre(noeud_enfant, niveau + 1, "", est_dernier_enfant, noeud_enfant.symbole)
            return
        
        # Déterminer les connecteurs pour l'affichage
        connecteur = "└── " if est_dernier else "├── "
        extension = "    " if est_dernier else "│   "

        # Afficher le noeud courant
        symbole_affiche = noeud.symbole
        
        if noeud.pointeurs:
            # Feuille avec pointeurs
            print(f"{prefixe}{connecteur}[{symbole_affiche}]")
            for i, pointeur in enumerate(noeud.pointeurs):
                est_dernier_pointeur = (i == len(noeud.pointeurs) - 1)
                connecteur_pointeur = "    └─→ " if est_dernier_pointeur else "    ├─→ "
                prefixe_pointeur = prefixe + extension if not est_dernier else prefixe + "    "
                print(f"{prefixe_pointeur}{connecteur_pointeur}{pointeur}")
        else:
            # Noeud interne
            print(f"{prefixe}{connecteur}{symbole_affiche}")
        
        # Afficher les enfants
        liste_enfants = list(noeud.enfants.values())
        for i, noeud_enfant in enumerate(liste_enfants):
            est_dernier_enfant = (i == len(liste_enfants) - 1)
            chemin_enfant = f"{chemin}/{noeud_enfant.symbole}"
            self.affichage_arbre(noeud_enfant, niveau + 1, prefixe + extension, est_dernier_enfant, chemin_enfant)

# Exemple d'utilisation
if __name__ == "__main__":
    import sys
    import os

    racine_projet = os.path.join(os.path.dirname(__file__), "..", "..")
    sys.path.append(os.path.abspath(racine_projet))

    from Util.TermStore.terme import FabriqueDeTermes

    dt = ArbreDeDiscrimination()

    terme1 = FabriqueDeTermes.creer_fonc("f", 2, [
        FabriqueDeTermes.creer_var("Y"),
        FabriqueDeTermes.creer_var("Z")
    ])

    terme2 = FabriqueDeTermes.creer_fonc("f", 2, [
        FabriqueDeTermes.creer_var("Y"),
        FabriqueDeTermes.creer_cons("a")
    ])

    terme3 = FabriqueDeTermes.creer_fonc("f", 2, [
        FabriqueDeTermes.creer_fonc("g", 2, [
            FabriqueDeTermes.creer_var("X"),
            FabriqueDeTermes.creer_cons("a")
        ]),
        FabriqueDeTermes.creer_var("Y")
    ])

    terme4 = FabriqueDeTermes.creer_fonc("f", 2, [
        FabriqueDeTermes.creer_fonc("g", 2, [
            FabriqueDeTermes.creer_var("Z"),
            FabriqueDeTermes.creer_cons("a")
        ]),
        FabriqueDeTermes.creer_var("Y")
    ])

    dt.inserer(terme1, "terme1 : f(Y, Z)")
    dt.inserer(terme2, "terme2 : f(Y, a)")
    dt.inserer(terme3, "terme3 : f(g(X, a), Y)")
    dt.inserer(terme4, "terme4 : f(g(Z, a), Y)")

    terme_recherche = FabriqueDeTermes.creer_fonc("f", 2, [
        FabriqueDeTermes.creer_var("X"),
        FabriqueDeTermes.creer_var("X")
    ])

    dt.affichage_arbre()

    print("\nRecherche de termes unifiables avec : f(X, X)")
    resultats = dt.rechercher_terme(terme_recherche)
    if not resultats:
        print("  Aucun terme unifiable trouvé.")
    else:
        for i, res in enumerate(resultats, 1):
            print(f"\n  Résultat {i} :")
            print(f"    Pointeurs    : {res.pointeurs}")
            if res.substitution:
                print(f"    Substitution :")
                for var, seq in res.substitution.items():
                    print(f"      {var}  →  {''.join(seq)}")
            else:
                print(f"    Substitution : ∅  (termes identiques)")


    """

    # Exemple du papier "Term Indexing" + unification impossible avec f(X, X) :

    # f(g(a, X), c)
    terme1 = FabriqueDeTermes.creer_fonc("f", 2, [
        FabriqueDeTermes.creer_fonc("g", 2, [
            FabriqueDeTermes.creer_cons("a"),
            FabriqueDeTermes.creer_var("X")
        ]),
        FabriqueDeTermes.creer_cons("c")
    ])

    # f(g(X, b), Y)
    terme2 = FabriqueDeTermes.creer_fonc("f", 2, [
        FabriqueDeTermes.creer_fonc("g", 2, [
            FabriqueDeTermes.creer_var("X"),
            FabriqueDeTermes.creer_cons("b")
        ]),
        FabriqueDeTermes.creer_var("Y")
    ])

    # f(g(a, b), a)
    terme3 = FabriqueDeTermes.creer_fonc("f", 2, [
        FabriqueDeTermes.creer_fonc("g", 2, [
            FabriqueDeTermes.creer_cons("a"),
            FabriqueDeTermes.creer_cons("b")
        ]),
        FabriqueDeTermes.creer_cons("a")
    ])

    # f(g(x, c), b)
    terme4 = FabriqueDeTermes.creer_fonc("f", 2, [
        FabriqueDeTermes.creer_fonc("g", 2, [
            FabriqueDeTermes.creer_var("X"),
            FabriqueDeTermes.creer_cons("c")
        ]),
        FabriqueDeTermes.creer_cons("b")
    ])

    # f(X, Y)
    terme5 = FabriqueDeTermes.creer_fonc("f", 2, [
        FabriqueDeTermes.creer_var("X"),
        FabriqueDeTermes.creer_var("Y")
    ])

    # f(X, X)
    terme6 = FabriqueDeTermes.creer_fonc("f", 2, [
        FabriqueDeTermes.creer_var("X"),
        FabriqueDeTermes.creer_var("X")
    ])

    # Insertion des termes dans l'arbre
    dt.inserer(terme1, "terme1 : f(g(a, X), c)")
    dt.inserer(terme2, "terme2 : f(g(X, b), Y)")
    dt.inserer(terme3, "terme3 : f(g(a, b), a)")
    dt.inserer(terme4, "terme4 : f(g(X, c), b)")
    dt.inserer(terme5, "terme5 : f(X, Y)")
    dt.inserer(terme6, "terme6 : f(X, X)")

    # Affichage
    dt.affichage_arbre()

    # Recherche des termes unifiable avec f(g(a, c), b)
    terme_a_rechercher = FabriqueDeTermes.creer_fonc("f", 2, [
        FabriqueDeTermes.creer_fonc("g", 2, [
            FabriqueDeTermes.creer_cons("a"),
            FabriqueDeTermes.creer_cons("c")
        ]),
        FabriqueDeTermes.creer_cons("b")
    ])

    print("\nRecherche de termes unifiables avec : f(g(a, c), b)")
    resultats = dt.rechercher_terme(terme_a_rechercher)
    if not resultats:
        print("  Aucun terme unifiable trouvé.")
    else:
        for i, res in enumerate(resultats, 1):
            print(f"\n  Résultat {i} :")
            print(f"    Pointeurs    : {res.pointeurs}")
            if res.substitution:
                print(f"    Substitution :")
                for var, seq in res.substitution.items():
                    print(f"      {var}  →  {' '.join(seq)}")
            else:
                print(f"    Substitution : ∅  (termes identiques)")
    """