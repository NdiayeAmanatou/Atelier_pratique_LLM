
from pathlib import Path
from pypdf import PdfReader


# Dossier contenant les documents PDF
DOSSIER_PDF = Path("data")


def extraire_documents():
    documents = []

    # Parcourir tous les PDF du dossier data
    fichiers_pdf = sorted(DOSSIER_PDF.glob("*.pdf"))

    for fichier in fichiers_pdf:
        print(f"Lecture du fichier : {fichier.name}")

        lecteur = PdfReader(str(fichier))

        # Lire chaque page séparément
        for numero, page in enumerate(lecteur.pages, start=1):
            texte = page.extract_text() or ""
            texte = texte.strip()

            # Ignorer les pages sans texte exploitable
            if not texte:
                continue

            documents.append({
                "texte": texte,
                "source": fichier.name,
                "page": numero,
            })

    return documents


if __name__ == "__main__":
    documents = extraire_documents()

    print("\n--- Résultat de l'extraction ---")
    print(f"Nombre de pages avec du texte : {len(documents)}")

    if documents:
        print("\nExemple de page extraite :")
        print("Source :", documents[0]["source"])
        print("Page :", documents[0]["page"])
        print("Texte :", documents[0]["texte"][:500])
