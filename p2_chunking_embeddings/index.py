import pandas as pd
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb

# --- Réglages ---
CHEMIN_DATASET = "data/dataset_nettoye.csv"
LONGUEUR_MIN = 60   # pages de moins de 60 caractères (après nettoyage) écartées
CHUNK_SIZE = 1500   # decoupage en caratere equivaut a 400 tokens
CHUNK_OVERLAP = 225. # le chevauchement en caractere equivaut a 60 tokens
MODELE = "intfloat/multilingual-e5-small"

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
#print(morceaux[0][-225:])

# le chevauchement (le début du deuxième)
#print(morceaux[1][:225])


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
# print(documents[100])
# print(metadatas[100])

# --- Embeddings : vérification de la longueur des chunks ---
model = SentenceTransformer(MODELE)

print("Longueur max du modèle (tokens) :", model.max_seq_length)

nb_tokens = [
    len(model.tokenizer.encode("passage: " + d, add_special_tokens=True))
    for d in documents
]

print("Nombre maximal de tokens :", max(nb_tokens))

print("Nombre de chunks dépassant 512 tokens :",
      sum(n > model.max_seq_length for n in nb_tokens))


# --- Génération des embeddings de tous les chunks ---

# Ajouter le préfixe passage: à chaque chunk
documents_prefixes = ["passage: " + d for d in documents]


# on Calcule les embeddings
embeddings = model.encode(
    documents_prefixes,
    batch_size=32,
    normalize_embeddings=True,
    show_progress_bar=True
)

# Vérification des résultats
print("Forme des embeddings :", embeddings.shape)
print("Nombre d'embeddings :", len(embeddings))
print("Dimensions d'un embedding :", embeddings.shape[1])


# --- Initialisation de ChromaDB ---

client = chromadb.PersistentClient(
    path="data/chroma_db"
)

collection = client.get_or_create_collection(
    name="corpus_llm",
    metadata={"hnsw:space": "cosine"}
)

print("Base vectorielle initialisée avec succès !")
print("Nom de la collection :", collection.name)
print("Nombre de documents :", collection.count())

# --- Insertion des données dans ChromaDB ---

collection.upsert(
    ids=ids,
    documents=documents,
    embeddings=embeddings.tolist(),
    metadatas=metadatas
)

print("Indexation terminée !")
print("Nombre de chunks enregistrés :", collection.count())

# peek() permet de consulter quelques éléments de la collection pour vérifier que les données ont bien été enregistrées.
print("Nombre d'embeddings enregistrés :",
      collection.count())

print("Exemple de document enregistré :",
      collection.peek(limit=1))

# Récupérer un élément de la collection (c'est juste une petite verification pour voir si la dimension d'un vecteur est bien respecte a 384)
exemple = collection.peek(limit=1)

print("Identifiant :", exemple["ids"][0])
print("Dimensions du vecteur :",
      exemple["embeddings"].shape[1])
print("Métadonnées :", exemple["metadatas"][0])