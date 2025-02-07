import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

import cards_scraping
import data_cleaning

import data_filter
import visualisation


# Wir brauchen eine Seitenleiste:
# Inhalt: - Startseite: Uebersicht ueber die Daten, Filteroptionen und suche, - Visualisierungen EDA:   , - Kartensuche bzw. Karten-Auswahl und aehnliche Karten bekommen. Create a Card and get suggestions

st.set_page_config(layout="wide")

def load_data():
    data_raw = cards_scraping.get_staples(cards_scraping.make_it_dataframe())
    data, image_links = data_cleaning.wholesome_cleaning(data_raw)
    
    data = data
    image_links = image_links
    
    if "data" not in st.session_state:
        st.session_state['data'] = data

    if "image_links" not in st.session_state:
        st.session_state['image_links'] = image_links


but_data_load = st.button('Load Data')
    
if "data" not in st.session_state:
    st.write("Please Load the data via the 'Load Data' Button.")



st.title("Yu-Gi-Oh App V0.12")

st.info("""
This is a work in progress Yu-Gi-Oh streamlit App. For now you can search for cards, filter them and view them. Planned is some visualisations, a create-a-card withsuggestions    what to choose and a deck-list printer.
""")


pages = {
    "1. Card Search"   : data_filter,
    "2. Visualisieren" : visualisation
}

# Erstelle eine Seitenleiste für die Navigation im Projekt
st.sidebar.title("Navigation")
select = st.sidebar.radio("Gehe zu:", list(pages.keys()))

if but_data_load:
    load_data()
    
if "data" in st.session_state:  
        
    # Starte die ausgewählte Seite
    pages[select].app(st.session_state['data'], st.session_state['image_links'])