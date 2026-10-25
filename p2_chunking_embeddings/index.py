import pandas as pd
from langchain_text_splitters import RecursiveCharacterTextSplitter

# --- Réglages ---
CHEMIN_DATASET = "data/dataset_nettoye.csv"
LONGUEUR_MIN = 60   # pages de moins de 60 caractères (après nettoyage) écartées
CHUNK_SIZE = 1600   # decoupage en caratere equivaut a 400 tokens
CHUNK_OVERLAP = 240. # le chevauchement en caractere equivaut a 60 tokens

# --- Chargement du dataset ---
df = pd.read_csv(CHEMIN_DATASET)

# --- Nettoyage : en-tête répété, numéro de diapositive, lignes de crédit d'image ---
MOTIF_ENTETE = r"^\s*Introduction\s+Attaques(?:\s+Pare-feux)?(?:\s+Détection\s+d['’]intrusion)?(?:\s+Authentification)?\s*"
MOTIF_PIED = r"\s*\d{1,3}\s*/\s*\d{1,3}\s*$"
MOTIF_CREDIT = r"(?m)^\s*Crédit\b[^\n]*\n?"

df["texte_propre"] = (
    df["texte"]
    .str.replace(MOTIF_ENTETE, "", regex=True)
    .str.replace(MOTIF_PIED, "", regex=True)
    .str.replace(MOTIF_CREDIT, "", regex=True)
    .str.strip()
)

# --- Contrôle du nettoyage ---
print("Pages qui avaient l'en-tête :", df["texte"].str.match(MOTIF_ENTETE).sum())
print("Pages qui commencent encore par le sommaire :",
      df["texte_propre"].str.contains(r"^\s*Introduction\s+Attaques", regex=True).sum())
print("Pages qui finissent encore par 'n / m' :",
      df["texte_propre"].str.contains(r"\d+\s*/\s*\d+\s*$", regex=True).sum())
print("Caractères retirés :", df["texte"].str.len().sum() - df["texte_propre"].str.len().sum())
print("Lignes 'Crédit' par document :")
print(df.groupby("titre")["texte"].apply(lambda s: s.str.count(r"(?m)^\s*Crédit\b").sum()))

# --- Filtre : écarter les pages presque vides ---
pd.set_option("display.max_colwidth", 120)
longueur = df["texte_propre"].str.len()
ecartees = df[longueur < LONGUEUR_MIN]
print("Pages écartées :", len(ecartees))
print(ecartees.assign(longueur=longueur)[["titre", "page", "longueur", "texte_propre"]]
      .sort_values("longueur", ascending=False).head(15).to_string())

df = df[longueur >= LONGUEUR_MIN].reset_index(drop=True)
print("Pages conservées :", len(df))

# --- Métadonnées : remplacer les valeurs vides ---
for col in ["auteur", "organisme", "date_publication"]:
    df[col] = df[col].fillna("inconnu")

print("Valeurs vides restantes par colonne :")
print(df[["titre", "source", "page", "url", "auteur", "organisme", "date_publication"]].isna().sum())

 
# creation du decoupeur 
splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)

#idx = df["texte_propre"].str.len().idxmax() # choix page la plus longue 
#texte = df.loc[idx, "texte_propre"] # recuperation de son texte
#morceaux = splitter.split_text(texte)  # donne une liste de chunks

#print("la longueur de la page :\n", len(texte))
#print("le nombre de chunks :\n", len(morceaux))
#print("la longueur de chaque chunk :\n", [len(m) for m in morceaux])

# le chevauchement (la fin du premier chunk)
#print(morceaux[0][-240:])

# le chevauchement (le début du deuxième)
#print(morceaux[1][:240])

# --- Découpage de toutes les pages en chunks ---
ids = []
documents = []
metadatas = []

for _, ligne in df.iterrows():
    morceaux = splitter.split_text(ligne["texte_propre"])
    for k, morceau in enumerate(morceaux):
        ids.append(f"{ligne['id']}_{k}")
        documents.append(morceau)
        metadatas.append({
            "titre": ligne["titre"],
            "source": ligne["source"],
            "page": int(ligne["page"]),
            "url": ligne["url"],
            "auteur": ligne["auteur"],
            "organisme": ligne["organisme"],
            "date_publication": ligne["date_publication"],
            "chunk": k,
        })

print("Nombre total de chunks :", len(documents))
print("Identifiants uniques :", len(set(ids)) == len(ids))
print("Trois listes de même longueur :", len(ids) == len(documents) == len(metadatas))
print(pd.Series([len(d) for d in documents]).describe())

print("--- Exemple : chunk n°100 ---")
print(documents[100])
print(metadatas[100])

