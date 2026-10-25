import pandas as pd

# --- Réglages ---
CHEMIN_DATASET = "data/dataset_nettoye.csv"
LONGUEUR_MIN = 60   # pages de moins de 60 caractères (après nettoyage) écartées

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