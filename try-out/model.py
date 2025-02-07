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

def knn_model(df):
    # Daten vorbereiten fuer Machine-Learning, Auswahl der Features:
    data = df

    numerical_features = ['atk', 'def', 'level', 'linkval', 'scale']
    categorical_features = ['race', 'attribute', 'frameType']


    df_numeric = data[numerical_features].fillna(0)
    df_categorical = pd.get_dummies(data[categorical_features]) #One Hot Encoding


    # Skalieren der numerischen Werte
    scaler = StandardScaler()
    df_numeric_scaled = scaler.fit_transform(df_numeric)


    # Kombinieren zu Vektorraum
    df_features = np.hstack((df_numeric_scaled, df_categorical.values))
    # knn fuer numerische aehnlichkeit

    knn = NearestNeighbors(n_neighbors=6, metric="cosine")
    knn.fit(df_features)

    return knn, df_features




def knn_model_spells_traps(df):
    # Daten vorbereiten fuer Machine-Learning, Auswahl der Features:
    data = df.loc[df['frameType'].isin(['spell', 'trap'])]

    categorical_features = ['race', 'frameType']


    df_categorical = pd.get_dummies(data[categorical_features]) #One Hot Encoding


    # knn fuer numerische aehnlichkeit

    knn = NearestNeighbors(n_neighbors=6, metric="cosine")
    knn.fit(df_categorical)

    return knn, df_categorical


def knn_model_monster(df):
    # Daten vorbereiten fuer Machine-Learning, Auswahl der Features:
    data = df.loc[df['frameType'].isin(['spell', 'trap']) == False]

    numerical_features = ['atk', 'def', 'level', 'linkval', 'scale']
    categorical_features = ['race', 'attribute', 'frameType']


    df_numeric = data[numerical_features].fillna(0)
    df_categorical = pd.get_dummies(data[categorical_features]) #One Hot Encoding


    # Skalieren der numerischen Werte
    scaler = StandardScaler()
    df_numeric_scaled = scaler.fit_transform(df_numeric)


    # Kombinieren zu Vektorraum
    df_features = np.hstack((df_numeric_scaled, df_categorical.values))
    # knn fuer numerische aehnlichkeit

    knn = NearestNeighbors(n_neighbors=6, metric="cosine")
    knn.fit(df_features)

    return knn, df_features



def effect_similarity_monster(df):
    data = df.loc[df['frameType'].isin(['spell', 'trap']) == False]

    # Effekttextverarbeitung
    tfidf = TfidfVectorizer(stop_words="english")
    text_matrix = tfidf.fit_transform(data['desc'].fillna(""))
    # Cosine Similarity berechnen
    text_similarity = cosine_similarity(text_matrix)

    return text_similarity

def effect_similarity_spell_trap(df):
    data = df.loc[df['frameType'].isin(['spell', 'trap'])]

    # Effekttextverarbeitung
    tfidf = TfidfVectorizer(stop_words="english")
    text_matrix = tfidf.fit_transform(data['desc'].fillna(""))
    # Cosine Similarity berechnen
    text_similarity = cosine_similarity(text_matrix)

    return text_similarity


def find_similar_cards(df, card_name, alpha=0.5):
    data = adapt_dtypes(df)
    
    frame_type_value = data.loc[data['name'] == card_name, 'frameType']
    
    # Überprüfe, ob die Karte existiert und ihren frameType bestimmen
    if frame_type_value.empty:
        raise ValueError(f"Karte '{card_name}' nicht gefunden!")
    
    frame_type = frame_type_value.iloc[0]
    
    # Je nach Kartentyp das passende Modell und die Textähnlichkeit verwenden
    if frame_type in ['spell', 'trap']:
        knn, df_features = knn_model_spells_traps(data)
        text_similarity = effect_similarity_spell_trap(data)
    else:
        knn, df_features = knn_model_monster(data)
        text_similarity = effect_similarity_monster(data)
    
    # Finde die Indexposition der Karte
    card_index = data[data["name"] == card_name].index[0]
    
    # Berechne numerische Ähnlichkeit
    distances, indices = knn.kneighbors(df_features[card_index:card_index+1])
    numerical_similarity = 1 / (1 + distances[0])  # Umkehren der Distanz, damit höher = ähnlicher
    
    # Hole Text-Ähnlichkeiten
    text_sim_scores = text_similarity[card_index]
    
    # Kombiniere beide Scores
    combined_similarity = alpha * numerical_similarity + (1 - alpha) * text_sim_scores[indices[0]]
    
    # Finde die Top 5 Karten
    sorted_indices = indices[0][np.argsort(combined_similarity)[::-1]]
    
    # Die resultierenden Karten nach `frameType` des Original-Frames filtern
    similar_6 = data.iloc[sorted_indices][['name', 'frameType']]

    # Filtere nur Karten des gleichen Typs wie die ausgewählte Karte (Monster oder Spell/Trap)
    similar_6_same_type = similar_6[similar_6['frameType'] == frame_type]

    # Verhindere, dass die ursprüngliche Karte in der Ausgabe erscheint
    similar_wo_own = similar_6_same_type[similar_6_same_type['name'] != card_name]

    return similar_wo_own


