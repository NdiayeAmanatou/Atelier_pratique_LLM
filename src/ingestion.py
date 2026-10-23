
from pathlib import Path
import re
import unicodedata
import pandas as pd
from pypdf import PdfReader


# 1. Définir les chemins du projet
RACINE = Path(__file__).resolve().parent.parent
DOSSIER_PDF = RACINE / "data"

FICHIER_BRUT = DOSSIER_PDF / "dataset_brut.csv"
FICHIER_NETTOYE = DOSSIER_PDF / "dataset_nettoye.csv"


# 2. Métadonnées des cinq documents PDF
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


# 3. Nettoyer le texte extrait
def nettoyer_texte(texte):
    """Nettoyer les caractères et espaces connus dans le corpus."""

    texte = unicodedata.normalize("NFKC", texte)

        # Corriger les accents aigus mal extraits des PDF.
    accents = {
        "a": "á", "e": "é", "i": "í", "o": "ó", "u": "ú",
        "A": "Á", "E": "É", "I": "Í", "O": "Ó", "U": "Ú",
    }

    # Exemple : "l’ ́epreuve" -> "l’épreuve"
    # Exemple : "4 ́etats" -> "4 états"
    texte = re.sub(
        r"([A-Za-z0-9’'])\s*\u0301\s*([aeiouAEIOU])",
        lambda m: m.group(1) + accents[m.group(2)],
        texte,
    )

    # Exemple : " ́Etape" -> "Étape"
    texte = re.sub(
        r"\u0301\s*([aeiouAEIOU])",
        lambda m: accents[m.group(1)],
        texte,
    )

    # Exemple : "utilise ́" -> "utilisé"
    texte = re.sub(
        r"([aeiouAEIOU])\s*\u0301",
        lambda m: accents[m.group(1)],
        texte,
    )

    # Corriger les cédilles mal extraites.
    # Exemple : "conc ̧u" -> "conçu"
    texte = re.sub(r"([cC])\s*\u0327", r"\1̧", texte)

    # Exemple : "re ̧ cu" -> "reçu"
    texte = re.sub(r"\s*\u0327\s*([cC])", r"̧\1", texte)

    # Réunir les caractères accentués lorsque c'est possible.
    texte = unicodedata.normalize("NFC", texte)
        # Corriger les accents aigus mal extraits des PDF.
    accents_aigus_unicode = {
        "a": "á",
        "e": "é",
        "i": "í",
        "o": "ó",
        "u": "ú",
        "A": "Á",
        "E": "É",
        "I": "Í",
        "O": "Ó",
        "U": "Ú",
    }

    # Exemple : "D ́etection" devient "Détection".
    texte = re.sub(
    r"([A-Za-z])\s+\u0301\s*([aeiouAEIOU])",
    lambda m: m.group(1) + accents_aigus_unicode[m.group(2)],
    texte,
    )

    # Uniformiser la représentation Unicode des caractères.
    texte = unicodedata.normalize("NFC", texte)
    texte = texte.replace("\x00", "")
    texte = texte.replace("\u00a0", " ")
    texte = texte.replace("\u200b", "")
    texte = texte.replace("\ufeff", "")

    # Corriger certains accents mal extraits
    accents_aigus = {
        "a": "á", "e": "é", "i": "í",
        "o": "ó", "u": "ú",
        "A": "Á", "E": "É", "I": "Í",
        "O": "Ó", "U": "Ú",
    }
    texte = re.sub(
        r"´\s*([aeiouAEIOU])",
        lambda m: accents_aigus[m.group(1)],
        texte,
    )

    accents_graves = {
        "a": "à", "e": "è", "u": "ù",
        "A": "À", "E": "È", "U": "Ù",
    }
    texte = re.sub(
        r"`\s*([aeuAEU])",
        lambda m: accents_graves[m.group(1)],
        texte,
    )

    # Corrections ciblées observées dans les PDF
    corrections = {
        "4Détection d’intrusion": "4 Détection d’intrusion",
        "séances decours": "séances de cours",
        "re¸ cu": "reçu",
        "re¸cu": "reçu",
        "D étection": "Détection",
        "entit é": "entité",
        "entitéafin": "entité afin",
        "l’accèsà": "l’accès à",
        "Entitésà": "Entités à",
        "seulélément": "seul élément",
        "deuxéléments": "deux éléments",
        "carteà puce": "carte à puce",
        "Introductionà": "Introduction à",
        "contrˆole": "contrôle",
    }

    for ancien, nouveau in corrections.items():
        texte = texte.replace(ancien, nouveau)

    # Normaliser les espaces sans supprimer les séparations utiles
    texte = re.sub(r"[ \t]+", " ", texte)
    texte = re.sub(r"\n[ \t]*\n(?:[ \t]*\n)+", "\n\n", texte)

    return texte.strip()


# 4. Extraire les PDF une seule fois
def extraire_donnees():
    donnees_brutes = []
    documents_nettoyes = []
    identifiant = 1

    fichiers_pdf = sorted(DOSSIER_PDF.glob("*.pdf"))

    if not fichiers_pdf:
        print(f"Aucun PDF trouvé dans : {DOSSIER_PDF}")
        return donnees_brutes, documents_nettoyes

    for fichier in fichiers_pdf:
        print(f"Lecture du fichier : {fichier.name}")

        metadonnees = METADONNEES.get(fichier.name, {})
        lecteur = PdfReader(str(fichier))

        for numero, page in enumerate(lecteur.pages, start=1):
            texte_brut = page.extract_text() or ""

            # Ignorer les pages sans texte extrait
            if not texte_brut.strip():
                continue

            texte_nettoye = nettoyer_texte(texte_brut)

            # Métadonnées communes aux deux datasets
            informations = {
                "id": identifiant,
                "titre": metadonnees.get("titre", fichier.stem),
                "auteur": metadonnees.get("auteur"),
                "organisme": metadonnees.get("organisme"),
                "date_publication": metadonnees.get("date"),
                "source": fichier.name,
                "page": numero,
                "url": metadonnees.get("url"),
            }

            # Dataset brut : texte avant nettoyage
            donnees_brutes.append({
                **informations,
                "texte": texte_brut,
            })

            # Dataset nettoyé : texte après nettoyage
            if texte_nettoye:
                documents_nettoyes.append({
                    **informations,
                    "texte": texte_nettoye,
                })

            identifiant += 1

    return donnees_brutes, documents_nettoyes


# 5. Fonction conservée pour le pipeline RAG existant
def extraire_documents():
    """Retourner les documents nettoyés pour le pipeline RAG."""

    _, documents_nettoyes = extraire_donnees()

    # Conserver les clés attendues par l'ancien code
    documents_rag = []

    for document in documents_nettoyes:
        documents_rag.append({
            "texte": document["texte"],
            "source": document["source"],
            "page": document["page"],
            "titre": document["titre"],
            "auteur": document["auteur"],
            "organisme": document["organisme"],
            "date": document["date_publication"],
            "url": document["url"],
        })

    return documents_rag


# 6. Créer les deux CSV quand on exécute ce fichier
def main():
    DOSSIER_PDF.mkdir(parents=True, exist_ok=True)

    donnees_brutes, documents_nettoyes = extraire_donnees()

    if not donnees_brutes:
        print("Aucune donnée extraite. Vérifie les PDF dans le dossier data.")
        return

    colonnes = [
        "id",
        "titre",
        "auteur",
        "organisme",
        "date_publication",
        "source",
        "page",
        "url",
        "texte",
    ]

    df_brut = pd.DataFrame(donnees_brutes, columns=colonnes)
    df_nettoye = pd.DataFrame(documents_nettoyes, columns=colonnes)

    df_brut.to_csv(FICHIER_BRUT, index=False, encoding="utf-8-sig")
    df_nettoye.to_csv(FICHIER_NETTOYE, index=False, encoding="utf-8-sig")

    print("\n--- Résultat de la préparation des données ---")
    print(f"Dataset brut créé : {FICHIER_BRUT}")
    print(f"Dataset nettoyé créé : {FICHIER_NETTOYE}")
    print(f"Pages extraites : {len(df_brut)}")
    print(f"Pages conservées après nettoyage : {len(df_nettoye)}")
    print(f"URL manquantes : {df_brut['url'].isna().sum()}")
    print(
        "Dates manquantes : "
        f"{df_brut['date_publication'].isna().sum()}"
    )

    print("\n--- Exemple de données nettoyées ---")
    print(
        df_nettoye[["source", "page", "texte"]]
        .head(3)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
