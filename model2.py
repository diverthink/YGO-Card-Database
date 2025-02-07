import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors


def adapt_dtypes(df):
    '''
    Passt die Kategorien nochmal an
    '''
    data = df
    data['attribute'] = data['attribute'].astype('category')
    data['frameType'] = data['frameType'].astype('category')
    data['type'] = data['type'].astype('category')
    data['staple'] = data['staple'].astype(bool)
    data['is_pendulum'] = data['is_pendulum'].astype(bool)
    data['tcg_date'] = pd.to_datetime(data['tcg_date'], errors='coerce')

    return data


def monster_data(df):
    data = df.loc[df['frameType'].isin(['spell', 'trap']) == False]
    data = data.reset_index(drop=True)

    return data

def spell_trap_data(df):
    data = df.loc[df['frameType'].isin(['spell', 'trap'])]
    data = data.reset_index(drop=True)

    return data


def knn_model_monster(df):
    '''
    Berechnet den KNN-Algorithmus für numerische Ähnlichkeit.
    '''
    numerical_features = ['atk', 'def', 'level', 'linkval', 'scale']
    categorical_features = ['race', 'attribute', 'frameType']

    df_numeric = df[numerical_features].fillna(0)
    df_categorical = pd.get_dummies(df[categorical_features])  # One-Hot-Encoding

    # Skalieren der numerischen Werte
    scaler = StandardScaler()
    df_numeric_scaled = scaler.fit_transform(df_numeric)

    # Kombinieren von numerischen und kategorischen Features
    df_features = np.hstack((df_numeric_scaled, df_categorical.values))

    # KNN-Modell für numerische Ähnlichkeit
    knn = NearestNeighbors(n_neighbors=len(df), metric="cosine")
    knn.fit(df_features)

    return knn, df_features


def knn_model_spell_trap(df):
    '''
    Berechnet den KNN-Algorithmus für numerische Ähnlichkeit.
    '''
    
    categorical_features = ['race', 'frameType']

    
    df_categorical = pd.get_dummies(df[categorical_features])  # One-Hot-Encoding

    # Skalieren der numerischen Werte
    scaler = StandardScaler()
    df_numeric_scaled = scaler.fit_transform(df_categorical)

    # Kombinieren von numerischen und kategorischen Features
    df_features = np.hstack((df_numeric_scaled, df_categorical.values))

    # KNN-Modell für numerische Ähnlichkeit
    knn = NearestNeighbors(n_neighbors=len(df), metric="cosine")
    knn.fit(df_features)

    return knn, df_features


def effect_similarity(df):
    '''
    Berechnet die Textähnlichkeit basierend auf dem Effekttext der Karten.
    '''
    tfidf = TfidfVectorizer(stop_words="english")
    text_matrix = tfidf.fit_transform(df['desc'].fillna(""))  # Effekttext der Karten

    # Berechnet die Cosine Similarity für den Effekttext
    text_similarity = cosine_similarity(text_matrix)

    return text_similarity


def find_similar_cards(df, card_name, alpha=0.5):
    '''
    Berechnet für eine gegebene Karte die Ähnlichkeit zu allen anderen Karten im DataFrame
    unter Verwendung einer Kombination aus KNN und Textähnlichkeit.
    '''
    data = adapt_dtypes(df)
    
    
    
    frame_type_value = data.loc[data['name'] == card_name, 'frameType']
    frame_type = frame_type_value.iloc[0]

    if frame_type in ['spell', 'trap']:
            data = spell_trap_data(data)
    
    else:
         data = monster_data(data)

    # Überprüfe, ob die Karte im DataFrame existiert
    if card_name not in data["name"].values:
        raise ValueError(f"Karte '{card_name}' nicht gefunden!")

    # Holen der Indexposition der Karte
    card_index = data[data["name"] == card_name].index[0]

    # KNN für numerische Ähnlichkeit
    if frame_type in ['spell', 'trap']:
        knn, df_features = knn_model_spell_trap(data)
    
    else:
         knn, df_features = knn_model_monster(data)

    # Berechne numerische Ähnlichkeit
    distances, indices = knn.kneighbors(df_features[card_index:card_index + 1])
    numerical_similarity = 1 / (1 + distances[0])  # Umkehren der Distanz, damit höhere Werte für größere Ähnlichkeit stehen

    # Textähnlichkeit berechnen
    text_similarity = effect_similarity(data)
    text_sim_scores = text_similarity[card_index]

    # Kombiniere numerische Ähnlichkeit und Textähnlichkeit
    combined_similarity = alpha * numerical_similarity + (1 - alpha) * text_sim_scores[indices[0]]

    # Karten nach der kombinierten Ähnlichkeit sortieren (absteigend)
    sorted_indices = indices[0][np.argsort(combined_similarity)[::-1]]

    # Erstelle eine Liste mit den 5 ähnlichsten Karten
    similar_cards = data.iloc[sorted_indices][['name', 'frameType']]
    similar_cards = similar_cards[similar_cards['name'] != card_name].head(5)

    return similar_cards