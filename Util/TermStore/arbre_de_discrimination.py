from typing import List, Dict, Any, Optional
from terme import NoeudTerme, ETIQUETTE_CONS, ETIQUETTE_VAR, DOMAINE_CONS


# TODO voir pour modifier la structure afin de garder les arités dispo dans l'arbre
# pour faciliter la gestion des calcules de profondeur etc.

class NoeudArbreDeDiscrimination:
    """
    Classe d'un noeud dans l'arbre de discrimination.

    Attributes:
        symbole (Optional[str]) : Symbole représentant le noeud (ex : X, f, a, etc.). 'None' pour le noeud racine.
        enfants (Dict[str, 'NoeudArbreDeDiscrimination']) : Noeuds enfants, indexés par leur symbole.
        pointeurs (List[Any]) : Pointeurs vers les termes associés à ce noeud.
    """
    def __init__(self, symbole: Optional[str] = None) -> None:
        self.symbole = symbole # Symbole du noeud (None pour la racine)
        self.enfants = {} # Noeuds enfants
        self.pointeurs = [] # Pointeurs vers les termes associés à ce noeud


class ArbreDeDiscrimination:
    """
    Arbre de discrimination pour stocker des termes.
    (Et par la suite chercher des termes unifiables.)
    
    Attributes:
        racine ('NoeudArbreDeDiscrimination') : Noeud racine de l'arbre. 'None' par défaut
    """
    
    def __init__(self) -> None:
        self.racine = NoeudArbreDeDiscrimination()

    def inserer(self, terme: NoeudTerme, pointeur: Any) -> None:
        """
        Insère un terme dans l'arbre de discrimination avec un pointeur associé.

        Le terme est parcouru en ordre préfixe pour créer un seul chemin dans l'arbre.
        Par exemple, f(X, g(Y)) crée le chemin : f -> *1 -> g -> *2

        Args:
            terme (NoeudTerme) : Le terme à insérer dans l'arbre.
            pointeur (Any): Un pointeur à associer avec ce terme.
        """
        var_map = {}
        # Mise à plat du terme en une séquence de symboles issue d'un parcours préfixe
        # On normalise aussi les variables
        sequence = self._mise_a_plat(terme, var_map)
        
        # Insertion dans l'arbre
        noeud_courant = self.racine
        for symbole in sequence:
            if symbole not in noeud_courant.enfants:
                noeud_courant.enfants[symbole] = NoeudArbreDeDiscrimination(symbole)
            noeud_courant = noeud_courant.enfants[symbole]
        
        # Ajout du pointeur au noeud feuille
        if pointeur not in noeud_courant.pointeurs:
            noeud_courant.pointeurs.append(pointeur)

    def _mise_a_plat(self, terme: NoeudTerme, var_map: Dict[str, str]) -> List[str]:
        """
        Mise à plat d'un terme en une séquence de symboles en ordre préfixe.
        Les variables sont normalisées en *1, *2, etc.
        
        Pour f(X, g(Y)), retourne : ['f', '*1', 'g', '*2']
        
        Args:
            terme (NoeudTerme) : Le terme à aplatir.
            var_map (Dict[str, str]) : Mapping de normalisation des variables.
        Returns:
            List[str] : Séquence aplatie de symboles.
        """
        resultat = []
        
        # Ajout du symbole du terme courant
        if terme.etiquette == ETIQUETTE_VAR:
            # Si c'est une variable, on la normalise
            if terme.nom not in var_map: # Nouvelle variable rencontrée
                var_map[terme.nom] = f"*{len(var_map) + 1}"
            resultat.append(var_map[terme.nom])
        else:
            # Constante ou fonction, on ajoute le nom tel quel
            resultat.append(terme.nom)
        
        # Ajout des enfants
        if terme.etiquette not in [ETIQUETTE_CONS, ETIQUETTE_VAR]:
            for enfant in terme.enfants:
                resultat.extend(self._mise_a_plat(enfant, var_map))
        
        return resultat
    
    def rechercher_terme(self, terme: NoeudTerme) -> List[Any]:
        """
        Recherche les termes unifiables avec le terme donné dans l'arbre de discrimination.

        Args:
            terme (NoeudTerme) : Le terme à rechercher.
        Returns:
            List[Any] : Liste des pointeurs associés aux termes unifiables trouvés.
        """
        
        terme_mise_a_plat = self._mise_a_plat(terme, {})
        resultats = []

        arites = self._extraire_arites(terme, {}) # Pour gérer la profondeur avec variables etc.

        self._recherche_recursive(self.racine, terme_mise_a_plat, arites, 0, resultats)
        return resultats
    
    def _extraire_arites(self, terme: NoeudTerme, var_map: Dict[str, str]) -> List[int]:
        """
        Extrait les arités de chaque symbole dans l'ordre préfixe.
        Cela permet de savoir combien d'arguments à chaque fonction.

        Args:
            terme (NoeudTerme): Le terme dont on extrait les arités.
            var_map (Dict[str, str]): Mapping de normalisation des variables.

        Returns:
            List[int]: Liste des arités pour chaque symbole.
        """
        resultats = [] # Initialisation de la liste 

        # Arité du terme courant
        # Cas 1 : variable, normalisation et arité 0
        if terme.etiquette == ETIQUETTE_VAR:
            if terme.nom not in var_map:
                var_map[terme.nom] = f"*{len(var_map) + 1}"
            resultats.append(0) 
        # Cas 2 : constante, arité 0
        elif terme.etiquette == ETIQUETTE_CONS:
            resultats.append(0)
        # Cas 3 : fonction, arité = etiquette (d'après notre classe) 
        #         on ajoute aussi les arités des enfants
        else:
            resultats.append(terme.etiquette)

            # Extraction des arités des enfants
            for enfant in terme.enfants:
                resultats.extend(self._extraire_arites(enfant, var_map))

        return resultats
    
    def _recherche_recursive(self, noeud: NoeudArbreDeDiscrimination, sequence: List[str], arites: List[int], index: int,resultats: List[Any]) -> None:
        """
        Fonction récursive pour rechercher des termes unifiables dans l'arbre de discrimination.

        Args:
            noeud (NoeudArbreDeDiscrimination) : Noeud courant dans l'arbre.
            sequence (List[str]) : Séquence aplatie du terme recherché.
            arites (List[int]) : Liste des arités pour chaque symbole dans la séquence.
            index (int) : Index actuel dans la séquence.
            resultats (List[Any]) : Liste accumulant les pointeurs des termes unifiables trouvés.
        """
        # Cas de base : toute la séquence a été parcourue
        if index >= len(sequence):
            resultats.extend(noeud.pointeurs) # Ajouter les pointeurs du noeud courant
            return
            
        symbole_courant = sequence[index]
        arite_courante = arites[index]

        # Recherche dans les enfants du noeud courant
        for enfant in noeud.enfants.values():

            # Cas 1 : le symbole courant est le même que celui du noeud enfant
            if symbole_courant == enfant.symbole:
                self._recherche_recursive(enfant, sequence, arites, index + 1, resultats) # On continue à chercher dans cet enfant
            
            # Cas 2 : le symbole de la recherche est une variable
            #         on peut unifier avec n'importe quel sous-terme
            elif symbole_courant.startswith("*"):
                # On doit sauter tout le sous-terme indexé par cet enfant 
                profondeur_enfant = self._calculer_profondeur_noeud(enfant)
                nouvel_index = index + profondeur_enfant
                if nouvel_index <= len(sequence):
                    self._recherche_recursive(enfant, sequence, arites, nouvel_index, resultats)

            # Cas 3 : le symbole de l'enfant est une variable
            #         peut s'unifier avec le sous-terme courant de l'arbre
            elif enfant.symbole.startswith("*"):
                # On saute le sous-terme dans l'arbre
                profondeur_sequence = self._calculer_profondeur_depuis_index(arites, index)
                nouvel_index = index + profondeur_sequence
                if nouvel_index <= len(sequence):
                    self._recherche_recursive(enfant, sequence, arites, nouvel_index, resultats)

            # TODO gérer la gestion de variables non unifiable à la fin de la recherche !!
        
    def _calculer_profondeur_noeud(self, noeud: NoeudArbreDeDiscrimination) -> int:
        """
        Calcule la profondeur (nombre de symboles) du sous-terme représenté par ce noeud.

        Args:
            noeud (NoeudArbreDeDiscrimination) : Le noeud dont on veut calculer la profondeur.
        Returns:
            int : La profondeur du sous-terme (nombre total de symboles).
        """
        if noeud.symbole is None:
            return 0
            
        # Pour variables ou constante = 1
        if noeud.symbole.startswith("*") or noeud.symbole in DOMAINE_CONS: # TODO tricherie ????
            return 1
            
        # Pour fonction = 1 + profondeurs des args
        profondeur = 1
        for enfant in noeud.enfants.values():
            profondeur += self._calculer_profondeur_noeud(enfant)
            
        return profondeur
    
    def _calculer_profondeur_depuis_index(self, arites: List[int], index: int) -> int:
        """
        Calcule la profondeur du sous-terme commençant à l'index donné.
        
        Args:
            arites (List[int]) : Liste des arités pour chaque symbole.
            index (int) : L'index de départ dans la séquence.
        Returns:
            int : Le nombre de symboles formant le sous-terme.
        """
        if index >= len(arites):
            return 0
        
        arite = arites[index]
        
        # Si arité = 0 (variable ou constante), la profondeur est 1
        if arite == 0:
            return 1
        
        # Si arité > 0 (fonction), on compte 1 + profondeur de chaque argument
        profondeur = 1
        position_courante = index + 1
        
        for _ in range(arite):
            profondeur_arg = self._calculer_profondeur_depuis_index(arites, position_courante)
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
    from terme import FabriqueDeTermes

    dt = ArbreDeDiscrimination()

    # Exemple du papier "Term Indexing" :

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

    # Insertion des termes dans l'arbre
    dt.inserer(terme1, "terme1 : f(g(a, X), c)")
    dt.inserer(terme2, "terme2 : f(g(X, b), Y)")
    dt.inserer(terme3, "terme3 : f(g(a, b), a)")
    dt.inserer(terme4, "terme4 : f(g(X, c), b)")
    dt.inserer(terme5, "terme5 : f(X, Y)")

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
    for res in resultats:
        print(f" - {res}")
