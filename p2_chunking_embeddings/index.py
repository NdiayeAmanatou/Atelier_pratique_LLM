import pandas as pd

# --- Réglages ---
CHEMIN_DATASET = "data/dataset_nettoye.csv"

# --- Chargement du dataset ---
df = pd.read_csv(CHEMIN_DATASET)

# --- Nettoyage : retirer l'en-tête répété et le numéro de diapositive ---
MOTIF_ENTETE = r"^\s*Introduction\s+Attaques\s+Pare-feux\s+Détection\s+d['’]intrusion\s+Authentification\s*"
MOTIF_PIED = r"\s*\d+\s*/\s*127\s*$"

df["texte_propre"] = (
    df["texte"]
    .str.replace(MOTIF_ENTETE, "", regex=True)
    .str.replace(MOTIF_PIED, "", regex=True)
    .str.strip()
)

# --- Contrôle du nettoyage ---
print("Pages qui avaient l'en-tête :", df["texte"].str.match(MOTIF_ENTETE).sum())
print("En-tête encore présent après nettoyage :",
      df["texte_propre"].str.contains(r"Pare-feux\s+Détection", regex=True).sum())
print("Caractères retirés :", df["texte"].str.len().sum() - df["texte_propre"].str.len().sum())
print("--- Page 1 nettoyée ---")
print(df.loc[0, "texte_propre"])
print("--- Page 11 nettoyée ---")
print(df.loc[10, "texte_propre"])