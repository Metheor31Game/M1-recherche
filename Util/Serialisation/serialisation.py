import os
from Util.Litteral.Litteral import Litteral


def serialiser(data, filename):
    """
    Serialise les prédicats dans un fichier texte.
    Version brute sans prétraitement
    
    Args:
        data: Une liste de prédicats (littéraux)
        filename: Le nom du fichier (sera dans Serialisation/Output/)
    
    Example:
        >>> litteraux = [Litteral("P", [X, Y]), Litteral("Q", [a])]
        >>> serialiser(litteraux, "predicats.txt")
        # Écrit: +P(X, Y).+Q(a).
    """
    outputDir = os.path.join(os.path.dirname(__file__), "Output")
    os.makedirs(outputDir, exist_ok=True)
    filepath = os.path.join(outputDir, filename)
    
    # Convertir chaque prédicat en string, la séparation se fait avec des points
    predicats_str = ".".join(str(pred) for pred in data) + "."
    
    with open(filepath, 'w') as f:
        f.write(predicats_str)

def deserialiser(filename):
    """
    Désérialise les prédicats depuis un fichier texte brut.

    Le format attendu est une suite de prédicats séparés par des points,
    par exemple: P(f(X,Y),a).Q(a).¬R(X).

    Args:
        filename: Le nom du fichier dans Serialisation/Output/

    Returns:
        list[Litteral]: Liste de prédicats sous forme d'objets Litteral.
    """
    outputDir = os.path.join(os.path.dirname(__file__), "Output")
    filePath = os.path.join(outputDir, filename)

    if not os.path.exists(filePath):
        raise FileNotFoundError(f"Fichier introuvable: {filePath}")

    with open(filePath, 'r') as f:
        contenu = f.read().strip()

    if not contenu:
        return []

    listPredicatStr = [pred.strip() for pred in contenu.split(".") if pred.strip()]
    listPredicat = [Litteral.from_string(pred) for pred in listPredicatStr]
    return listPredicat
