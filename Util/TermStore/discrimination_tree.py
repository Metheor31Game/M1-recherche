from typing import List, Dict, Any, Optional
from terme import NoeudTerme, ETIQUETTE_CONS, ETIQUETTE_VAR


class NoeudDiscriminationTree:
    """
    Classe d'un noeud dans l'arbre de discrimination.

    Attributs:
        symbole (Optional[str]): Symbole représentant le noeud (ex : X, f, a, etc.).
                                 'None' pour le noeud racine.
        enfants (Dict[str, 'NoeudDiscriminationTree']): Noeuds enfants, indexés par leur symbole.
        pointeurs (List[Any]): Pointeurs vers les termes associés à ce noeud.
    """
    def __init__(self, symbole: Optional[str] = None) -> None:
        self.symbole = symbole # Symbole du noeud (None pour la racine)
        self.enfants = {} # Noeuds enfants
        self.pointeurs = [] # Pointeurs vers les termes associés à ce noeud


class DiscriminationTree:
    """
    Discrimination tree pour stocker des termes.
    (Et par la suite chercher des termes unifiables.)
    
    Attributs:
        racine ('NoeudDiscriminationTree'): Noeud racine de l'arbre, 'None' par défaut
    """
    
    def __init__(self) -> None:
        """Initialise un arbre de discrimination vide."""
        self.racine = NoeudDiscriminationTree()

    def inserer(self, terme: NoeudTerme, pointeur: Any) -> None:
        """
        Insère un terme dans l'arbre de discrimination avec un pointeur associé.

        Le terme est parcouru en ordre préfixe pour créer un seul chemin dans l'arbre.
        Par exemple, f(X, g(Y)) crée le chemin : f -> *1 -> g -> *2

        Args:
            terme (NoeudTerme): Le terme à insérer dans l'arbre.
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
                noeud_courant.enfants[symbole] = NoeudDiscriminationTree(symbole)
            noeud_courant = noeud_courant.enfants[symbole]
        
        # Ajout du pointeur au noeud feuille
        if pointeur not in noeud_courant.pointeurs:
            noeud_courant.pointeurs.append(pointeur)

    def _mise_a_plat(self, terme: NoeudTerme, var_map: Dict[str, str]) -> List[str]:
        """
        Mise à plat d'un terme en une séquence de symboles en ordre préfixe.
        Les variables sont normalisées en *1, *2, etc.
        
        Pour f(X, g(Y)), retourne: ['f', '*1', 'g', '*2']
        
        Args:
            terme (NoeudTerme): Le terme à aplatir.
            var_map (Dict[str, str]): Mapping de normalisation des variables.
        Returns:
            List[str]: Séquence aplatie de symboles.
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
    
    def affichage_arbre(self, noeud: Optional[NoeudDiscriminationTree] = None, niveau: int = 0, prefixe: str = "", est_dernier: bool = True, chemin: str = "") -> None:
        """
        Affiche l'arbre de discrimination de manière lisible dans la console.
        Structure de la fonction générée par IA.
        
        Args:
            noeud (Optional['NoeudDiscriminationTree']): Le noeud courant à afficher. 'None' pour commencer à la racine.
            niveau (int): Niveau actuel dans l'arbre, utilisé pour l'indentation.
            prefixe (str): Chaîne de préfixe pour formater la structure de l'arbre.
            est_dernier (bool): Indique si le noeud courant est le dernier enfant de son parent.
            chemin (str): Le chemin vers le noeud courant.
        """
        if noeud is None:
            # Commencer à la racine
            noeud = self.racine
            print("╔" + "═" * 58 + "╗")
            print("║" + " " * 16 + "DISCRIMINATION TREE" + " " * 23 + "║")
            print("╚" + "═" * 58 + "╝")
            print("\nROOT")
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

    dt = DiscriminationTree()

    # terme1 : f(X, g(Y))
    term1 = FabriqueDeTermes.creer_fonc("f", 2, [
        FabriqueDeTermes.creer_var("X"),
        FabriqueDeTermes.creer_fonc("g", 1, [FabriqueDeTermes.creer_var("Y")])
    ])
    
    # terme2 : f(Z, g(W)) - Identique à terme1 mais avec d'autres variables
    term2 = FabriqueDeTermes.creer_fonc("f", 2, [
        FabriqueDeTermes.creer_var("Z"),
        FabriqueDeTermes.creer_fonc("g", 1, [FabriqueDeTermes.creer_var("W")])
    ])

    # terme3 : f(a, g(b)) - Instance concrète
    term3 = FabriqueDeTermes.creer_fonc("f", 2, [
        FabriqueDeTermes.creer_cons("a"),
        FabriqueDeTermes.creer_fonc("g", 1, [FabriqueDeTermes.creer_cons("b")])
    ])

    # terme4 : f(a, g(X)) - Partiellement concrète
    term4 = FabriqueDeTermes.creer_fonc("f", 2, [
        FabriqueDeTermes.creer_cons("a"),
        FabriqueDeTermes.creer_fonc("g", 1, [FabriqueDeTermes.creer_var("X")])
    ])

    # terme5 : f(X, Y) - très général
    term5 = FabriqueDeTermes.creer_fonc("f", 2, [
        FabriqueDeTermes.creer_var("X"),
        FabriqueDeTermes.creer_var("Y")
    ])

    # terme6 : f(Y, X) - Inverse des variables de terme5
    term6 = FabriqueDeTermes.creer_fonc("f", 2, [
        FabriqueDeTermes.creer_var("Y"),
        FabriqueDeTermes.creer_var("X")
    ])

    # Insertion des termes dans l'arbre
    dt.inserer(term1, "terme1 : f(X, g(Y))")
    dt.inserer(term2, "terme2 : f(Z, g(W))")
    dt.inserer(term3, "terme3 : f(a, g(b))")
    dt.inserer(term4, "terme4 : f(a, g(X))")
    dt.inserer(term5, "terme5 : f(X, Y)")
    dt.inserer(term6, "terme6 : f(Y, X)")

    # Affichage
    dt.affichage_arbre()

