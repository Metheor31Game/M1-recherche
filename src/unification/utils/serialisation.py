import os
import gzip
from .logique.litteral import Litteral


def serialiser(data, filename, compresser_fichier: bool = True):
    """
    Serialise les prédicats dans un fichier texte, compressé (gzip) ou non.
    Version brute sans prétraitement
    
    Args:
        data: Une liste de prédicats (littéraux)
        filename: Le nom du fichier (sera dans Serialisation/Output/)
        compresser_fichier: True pour écrire en gzip, False pour écrire en texte brut.
    
    Example:
        >>> litteraux = [Litteral("P", [X, Y]), Litteral("Q", [a])]
        >>> serialiser(litteraux, "predicats.txt.gz")
        # Écrit: +P(X, Y).+Q(a).
    """
    outputDir = os.path.join(os.path.dirname(__file__), "Output")
    os.makedirs(outputDir, exist_ok=True)
    filepath = os.path.join(outputDir, filename)
    
    # Convertir chaque prédicat en string, la séparation se fait avec des points
    predicats_str = ".".join(str(pred) for pred in data) + "."
    
    if compresser_fichier:
        compresser(predicats_str, filepath)
    else:
        with open(filepath, "wt", encoding="utf-8") as f:
            f.write(predicats_str)

def deserialiser(filename, decompresser_fichier: bool = True):
    """
    Désérialise les prédicats depuis un fichier texte, compressé (gzip) ou non.

    Le format attendu est une suite de prédicats séparés par des points,
    par exemple: P(f(X,Y),a).Q(a).¬R(X).

    Args:
        filename: Le nom du fichier dans Serialisation/Output/
        decompresser_fichier: True pour lire un fichier gzip, False pour lire un texte brut.

    Returns:
        list[Litteral]: Liste de prédicats sous forme d'objets Litteral.
    """
    outputDir = os.path.join(os.path.dirname(__file__), "Output")
    filePath = os.path.join(outputDir, filename)

    if not os.path.exists(filePath):
        raise FileNotFoundError(f"Fichier introuvable: {filePath}")

    if decompresser_fichier:
        contenu = decompresser(filePath).strip()
    else:
        with open(filePath, "rt", encoding="utf-8") as f:
            contenu = f.read().strip()

    if not contenu:
        return []

    listPredicatStr = [pred.strip() for pred in contenu.split(".") if pred.strip()]
    listPredicat = [Litteral.from_string(pred) for pred in listPredicatStr]
    return listPredicat

def compresser(data_str, path):
    with gzip.open(path, "wt", encoding="utf-8") as f:
        f.write(data_str)

def decompresser(path: str) -> str:
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return f.read()
