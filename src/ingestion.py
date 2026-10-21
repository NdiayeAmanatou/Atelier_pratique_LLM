
from pathlib import Path
import re

from pypdf import PdfReader


DOSSIER_PDF = Path("data")

# Métadonnées des documents décrits dans SOURCES.md
METADONNEES = {
    "cybersec.pdf": {
        "titre": "Introduction à la Cybersécurité",
        "auteur": "Rushed Kanawati",
        "organisme": "Université Sorbonne Paris Nord",
        "date": "janvier 2023",
        "url": "https://www-lipn.univ-paris13.fr/~kanawati/pdf/cybersec-CYU.pdf",
    },
    "CyberSecurity_Governance_Jan2020.pdf": {
        "titre": "Guide pour la bonne gouvernance de la cybersécurité",
        "auteur": None,
        "organisme": "DCAF",
        "date": "2019",
        "url": "https://www.dcaf.ch/sites/default/files/publications/documents/CyberSecurity_Governance_Jan2020.pdf.pdf",
    },
    "fondamentaux cybersecurite.pdf": {
        "titre": "Les fondamentaux de la cybersécurité",
        "auteur": None,
        "organisme": None,
        "date": "2017",
        "url": "https://www.cscglobal.com/cscglobal/pdfs/Essentials-for-Cyber-Security_FR.pdf",
    },
    "La cybersécurité dans les entités.pdf": {
        "titre": "La cybersécurité dans les entités des Nations Unies",
        "auteur": "Jorge Flores Callejas, Aicha Afifi et Nikolay Lozinskiy",
        "organisme": "Corps commun d'inspection des Nations Unies",
        "date": "2021",
        "url": "https://www.unjiu.org/sites/www.unjiu.org/files/jiu_rep_2021_3_french.pdf",
    },
    "manuel de cybersecurite.pdf": {
        "titre": "Manuel de cybersécurité pour les partis politiques",
        "auteur": None,
        "organisme": "National Democratic Institute (NDI)",
        "date": None,
        "url": "https://www.ndi.org/sites/default/files/%5BFrench%5D%20Cybersecurity%20Handbook%20for%20Political%20Parties-compressed_0.pdf",
    },
}


def nettoyer_texte(texte):
    """Nettoyer les espaces sans supprimer le contenu utile."""
    texte = texte.replace("\x00", "")
    texte = re.sub(r"[ \t]+", " ", texte)
    texte = re.sub(r"\n{3,}", "\n\n", texte)
    return texte.strip()


def extraire_documents():
    documents = []
    fichiers_pdf = sorted(DOSSIER_PDF.glob("*.pdf"))

    for fichier in fichiers_pdf:
        print(f"Lecture du fichier : {fichier.name}")

        lecteur = PdfReader(str(fichier))
        metadonnees = METADONNEES.get(fichier.name, {})

        for numero, page in enumerate(lecteur.pages, start=1):
            texte_brut = page.extract_text() or ""
            texte = nettoyer_texte(texte_brut)

            # Ignorer les pages sans texte exploitable
            if not texte:
                continue

            documents.append({
                "texte": texte,
                "source": fichier.name,
                "page": numero,
                "titre": metadonnees.get("titre", fichier.stem),
                "auteur": metadonnees.get("auteur"),
                "organisme": metadonnees.get("organisme"),
                "date": metadonnees.get("date"),
                "url": metadonnees.get("url"),
            })

    return documents


if __name__ == "__main__":
    documents = extraire_documents()

    print("\n--- Résultat de l'extraction ---")
    print(f"Nombre de pages avec du texte : {len(documents)}")

    if documents:
        exemple = documents[0]

        print("\n--- Exemple de page extraite ---")
        print("Source :", exemple["source"])
        print("Titre :", exemple["titre"])
        print("Page :", exemple["page"])
        print("Date :", exemple["date"])
        print("URL :", exemple["url"])
        print("Texte :", exemple["texte"][:500])
