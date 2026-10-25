 1. Justification du choix de la taille des chunks et du chevauchement

Pour le découpage des documents, nous avons utilisé les paramètres suivants :

```python
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 225
```

### 1.1. Taille des chunks : 1500 caractères

Le paramètre `CHUNK_SIZE` définit la taille maximale souhaitée pour chaque fragment de texte.

Nous avons choisi une taille de 1500 caractères afin de trouver un équilibre entre la conservation du contexte et la précision de la recherche.

En effet, des fragments trop courts risquent de séparer des informations qui sont liées entre elles. À l'inverse, des fragments trop longs peuvent regrouper plusieurs idées ou sujets différents, ce qui peut rendre la recherche de passages pertinents moins précise.

Une taille de 1500 caractères constitue donc un compromis adapté à notre corpus de documents sur la cybersécurité.

Il est important de préciser que cette valeur correspond à un nombre de caractères et non à un nombre de tokens.

### 1.2. Chevauchement : 225 caractères

Le paramètre `CHUNK_OVERLAP` définit le nombre de caractères communs entre deux fragments consécutifs.

Nous avons choisi un chevauchement de 225 caractères, soit 15 % de la taille d'un chunk.

Ce chevauchement permet de conserver une continuité entre les fragments. Il limite la perte de contexte lorsqu'une phrase ou une explication se trouve à la frontière entre deux fragments.

Il facilite également la recherche d'informations pertinentes, car une partie du contenu présent à la fin d'un fragment est répétée au début du fragment suivant.

### 1.3. Vérification de la compatibilité avec le modèle d'embedding

Le modèle `multilingual-e5-small` possède une longueur maximale de séquence de 512 tokens.

Après le découpage, nous avons donc vérifié le nombre de tokens de chaque fragment, en tenant compte du préfixe `passage:` utilisé pour générer les embeddings.

Les résultats obtenus sont les suivants :

- Longueur maximale autorisée : 512 tokens.
- Nombre maximal de tokens observé : 507.
- Nombre de fragments dépassant la limite : 0.

Cette vérification confirme que tous les fragments générés respectent la limite de séquence du modèle utilisé.

**Bilan :** les paramètres retenus permettent de conserver suffisamment de contexte dans chaque fragment, de limiter les ruptures entre les idées et de respecter la capacité du modèle d'embedding.

 2. Justification du choix du modèle d'embedding

Pour transformer les fragments de texte en vecteurs numériques, nous avons retenu le modèle :

```python
MODELE = "intfloat/multilingual-e5-small"
```

Nous avons choisi ce modèle plutôt que `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, car ses caractéristiques correspondent davantage aux besoins de notre système RAG.

### 2.1. Adaptation à la recherche sémantique

Le modèle `multilingual-e5-small` est conçu notamment pour les tâches de recherche d'informations et de récupération de passages pertinents.

Il permet de représenter les textes sous forme de vecteurs numériques afin de retrouver des passages proches d'une question par leur sens, même lorsque les mots utilisés sont différents.

Cette caractéristique est importante dans notre projet : lorsqu'un utilisateur pose une question sur la cybersécurité, le système doit retrouver les passages les plus pertinents dans notre corpus documentaire.

### 2.2. Prise en charge du français et des langues multiples

Le modèle prend en charge environ 100 langues, dont le français.

Cette capacité multilingue est adaptée à notre corpus actuel, constitué de documents en français, et offre une certaine flexibilité si le projet évolue vers des documents rédigés dans d'autres langues.

### 2.3. Comparaison avec paraphrase-multilingual-MiniLM-L12-v2

Le modèle `paraphrase-multilingual-MiniLM-L12-v2` est principalement orienté vers la représentation de phrases sémantiquement proches, notamment les paraphrases et la comparaison de similarité entre phrases.

Il peut également être utilisé pour effectuer de la recherche sémantique. Cependant, `multilingual-e5-small` présente un avantage pour notre cas d'utilisation : il est spécifiquement entraîné pour des tâches de recherche et de récupération de passages pertinents.

Une autre différence importante concerne la longueur des séquences :

- `multilingual-e5-small` accepte jusqu'à 512 tokens.
- `paraphrase-multilingual-MiniLM-L12-v2` utilise une longueur maximale de 128 tokens par défaut dans Sentence Transformers.

Or, nos fragments peuvent atteindre 507 tokens, préfixe compris. Le modèle E5 permet donc de traiter nos fragments sans dépasser sa limite de séquence, tandis que la configuration par défaut de MiniLM entraînerait la troncature d'une partie de nos fragments.

Les deux modèles produisent des embeddings de 384 dimensions. La différence de dimensions n'a donc pas constitué un critère de sélection.

### 2.4. Utilisation des préfixes query et passage

Le modèle E5 nécessite l'utilisation de préfixes adaptés au type de texte traité :

- `passage:` pour les fragments de documents à indexer ;
- `query:` pour les questions soumises par l'utilisateur.

Dans notre code, nous avons utilisé le préfixe `passage:` avant de générer les embeddings des fragments.

Lors de la recherche, le préfixe `query:` sera utilisé pour encoder les questions de l'utilisateur.

Cette distinction permet de respecter le fonctionnement prévu lors de l'entraînement du modèle pour les tâches de recherche question-document.

### 2.5. Bilan du choix

Nous avons retenu `multilingual-e5-small` pour son adaptation à la recherche sémantique, sa prise en charge du français, sa limite de 512 tokens et son fonctionnement spécifique avec les préfixes `query:` et `passage:`.

Ce choix est cohérent avec les besoins de notre système RAG, qui doit retrouver des passages pertinents dans un corpus documentaire afin de fournir des éléments de réponse à l'utilisateur.

Les performances réelles de ce choix pourront être évaluées à l'étape de recherche et d'évaluation du système.

Sources pour notre bibliographie :
- Fiche officielle du modèle multilingual-e5-small – Hugging Face.
- Documentation Sentence Transformers – Comparaison des modèles.
- Documentation Sentence Transformers – Modèles multilingues

 3. Justification du choix de ChromaDB

Pour stocker les embeddings générés et effectuer la recherche de similarité, nous avons choisi ChromaDB plutôt que FAISS.

### 3.1. Présentation des deux solutions

**ChromaDB** est une base de données vectorielle conçue pour stocker et rechercher des représentations vectorielles (*embeddings*). Elle permet également de conserver les textes, les identifiants et les métadonnées associés à chaque vecteur.

**FAISS (Facebook AI Similarity Search)** est une bibliothèque développée par Meta, spécialisée dans la recherche efficace de vecteurs similaires. Elle propose différents types d'index permettant d'optimiser les recherches selon le volume de données et les besoins en performance.

Les deux solutions permettent donc d'effectuer une recherche de similarité vectorielle, mais elles ne proposent pas le même niveau de gestion des données.

### 3.2. Raisons du choix de ChromaDB

Nous avons retenu ChromaDB pour les raisons suivantes :

**a) Stockage des textes et des embeddings**

ChromaDB permet de conserver dans une même collection les fragments de texte, leurs embeddings et leurs identifiants. Cette organisation facilite la récupération des passages originaux après une recherche vectorielle.

**b) Gestion des métadonnées**

Chaque fragment de notre corpus est associé à plusieurs métadonnées : titre, source, numéro de page, URL, auteur, organisme, date de publication et numéro du chunk.

ChromaDB permet de stocker directement ces informations avec chaque fragment. Elles pourront être utilisées dans la partie génération pour identifier les sources des passages récupérés.

**c) Persistance des données**

Nous avons utilisé `PersistentClient` pour assurer la conservation de la base vectorielle sur le disque :

```python
client = chromadb.PersistentClient(path="data/chroma_db")
```

Cette fonctionnalité permet de retrouver les données enregistrées après l'arrêt du programme, sans devoir reconstruire systématiquement la base vectorielle.

**d) Simplicité d'intégration dans le système RAG**

ChromaDB propose des fonctionnalités directement utilisables pour rechercher les vecteurs les plus proches d'une question, récupérer les textes correspondants et accéder à leurs métadonnées.

Cela facilite la continuité du développement entre la phase d'indexation et la phase de récupération des passages.

### 3.3. Pourquoi ne pas avoir choisi FAISS ?

FAISS est une solution performante pour la recherche de similarité vectorielle, notamment lorsqu'il faut gérer de très grands volumes d'embeddings ou optimiser les temps de recherche.

Cependant, dans notre projet, nous avons également besoin de gérer les textes originaux, les identifiants et les métadonnées associés aux embeddings.

Avec FAISS, ces informations doivent être organisées et conservées dans des structures complémentaires.

ChromaDB répond directement à ces besoins et permet donc de simplifier l'architecture de notre système.

### 3.4. Configuration de la base vectorielle

Nous avons créé une collection appelée `corpus_llm` et choisi la distance cosinus pour comparer les embeddings :

```python
collection = client.get_or_create_collection(
    name="corpus_llm",
    metadata={"hnsw:space": "cosine"}
)
```

La distance cosinus permet de comparer l'orientation des vecteurs afin d'évaluer leur proximité sémantique. Nos embeddings ayant été normalisés lors de leur génération, ce choix est cohérent avec notre méthode de représentation.

**Bilan :** ChromaDB a été retenu principalement pour sa simplicité d'utilisation, sa persistance intégrée, sa gestion des métadonnées et sa facilité d'intégration dans notre architecture RAG. FAISS reste une alternative pertinente, notamment pour des besoins de recherche vectorielle à grande échelle.

Sources documentaires
- Documentation ChromaDB – Collections.
- Documentation ChromaDB – Persistance.
- Documentation officielle FAISS.
- Documentation ChromaDB – Concepts.

 4. Justification du seuil minimal de longueur des pages

Pour éliminer les pages contenant trop peu de contenu exploitable, nous avons défini le paramètre suivant :

```python id="y3f9bb"
LONGUEUR_MIN = 60
```

Ce paramètre permet d'écarter les pages dont le texte nettoyé contient moins de 60 caractères.

### 4.1. Pourquoi filtrer les pages trop courtes ?

Les documents PDF de notre corpus ne contiennent pas uniquement des pages avec du contenu textuel exploitable.

Certaines pages peuvent contenir uniquement un titre, un numéro de page, une illustration, des crédits d'image ou quelques mots isolés.

Ces contenus apportent généralement peu d'informations utiles à la recherche documentaire.

Leur conservation pourrait entraîner la création d'embeddings à partir de textes trop courts ou insuffisamment informatifs.

Nous avons donc choisi d'appliquer un filtre minimal afin de conserver principalement les pages contenant une quantité suffisante de texte.

### 4.2. Pourquoi avoir choisi 60 caractères ?

Le seuil de 60 caractères constitue un choix empirique adapté à notre corpus.

Il permet d'écarter les textes très courts, qui correspondent souvent à des titres isolés, des numéros de page ou des contenus résiduels après nettoyage.

Ce seuil représente un compromis simple entre la réduction des contenus peu exploitables et la conservation des pages suffisamment développées pour participer à la recherche documentaire.

Il ne garantit cependant pas qu'un texte dépassant 60 caractères soit nécessairement pertinent.

### 4.3. Pourquoi appliquer le filtre après le nettoyage ?

Le filtrage est effectué après le nettoyage des textes afin de mesurer uniquement la longueur du contenu restant réellement exploitable.

En effet, les pages PDF peuvent contenir des éléments parasites tels que les numéros de page, les en-têtes répétitifs ou les crédits d'illustrations.

Si le filtrage était effectué avant le nettoyage, ces éléments pourraient artificiellement augmenter la longueur du texte et empêcher l'élimination de certaines pages peu informatives.

L'application du seuil après nettoyage permet donc d'obtenir une sélection plus cohérente avec le contenu réellement utilisé pour l'indexation.

### 4.4. Limites du seuil choisi

Ce filtrage repose uniquement sur le nombre de caractères et ne mesure pas directement la qualité sémantique du texte.

Une page courte peut contenir une information importante, tandis qu'une page longue peut contenir des informations peu pertinentes.

Le seuil de 60 caractères doit donc être considéré comme un filtre préliminaire de qualité, et non comme une garantie de pertinence.

**Bilan :** le seuil `LONGUEUR_MIN = 60` permet de réduire la présence de pages trop courtes ou peu informatives dans le corpus avant le découpage et la génération des embeddings.

5. RESULTATS OBTENUS : 
- Apres decoupage on obtient 965 chunks, 
- La dimensions de chaque vecteur est de 384 , 
- Le maximum est de 507 tokens et aucun chunks ne dépasse la limite de 512 tokens du modele.

6. UNE PRECISION : 
- ChromaDB stocke les embeddings et les métadonnées, mais la partie on doit récupérer les textes et métadonnées avec les résultats de recherche pour pouvoir les transmettre au modèle génératif.

- Les 384 correspondent au nombre de dimensions des vecteurs (embeddings) générés par notre modèle multilingual-e5-small.

Cette valeur vient directement de l'architecture du modèle pré-entraîné. Ce n'est pas une valeur que nous avons choisie ou définie dans notre code.
1. Qu'est-ce que cela signifie ?
Lorsque nous donnons un texte au modèle E5, celui-ci le transforme en un vecteur numérique composé de 384 nombres.

- À retenir : les 384 dimensions sont une caractéristique du modèle multilingual-e5-small. Elles représentent la taille du vecteur numérique utilisé pour représenter chaque fragment de texte et effectuer les recherches de similarité.