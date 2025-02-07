import pandas as pd
import streamlit as st
import model2
from datetime import datetime

    

def app(data: pd.DataFrame, image_links: pd.DataFrame):
    

    # Data import
    if "data" not in st.session_state:
        st.session_state['data'] = data

    if "image_links" not in st.session_state:
        st.session_state['image_links'] = image_links





    # General information

    con_general = st.container(border=False)

    with con_general:
        st.subheader('General information about the cards currently in the TCG', divider= True)
        display_count_id, display_count_type, display_count_frameType, display_count_attribute, display_count_race_trell, display_count_race_monster, display_count_archetype, display_count_staple, display_count_is_pendulum = st.columns(9)


        with display_count_id:
            st.markdown(f"**#IDs:** \n {len(st.session_state['data']['id'].unique())}")

        with display_count_type:
            st.markdown(f"**#Card Types:** \n {len(st.session_state['data']['type'].unique())}")

        with display_count_frameType:
            st.markdown(f"**#Frame Types:** \n {len(st.session_state['data']['frameType'].unique())}")

        with display_count_attribute:
            st.markdown(f"**#Attributes:** \n {len(st.session_state['data']['attribute'].unique())-1}")

        with display_count_race_trell:
            st.markdown(f"**#Spell/Trap Races:** \n {len(st.session_state['data'].loc[st.session_state['data']['race'].isin(['Continuous', 'Quick-Play', 'Equip', 'Normal', 'Field']), 'race'].unique())}")

        with display_count_race_monster:
            st.markdown(f"**#Monster Races:** \n {len(st.session_state['data'].loc[st.session_state['data']['race'].isin(['Beast', 'Insect', 'Fish', 'Field', 'Spellcaster', 'Machine', 'Ritual', 'Warrior', 'Fiend', 'Beast-Warrior', 'Rock', 'Fairy', 'Dragon', 'Sea Serpent', 'Aqua', 'Cyberse', 'Plant', 'Counter', 'Winged Beast', 'Wyrm', 'Pyro', 'Reptile', 'Zombie', 'Psychic', 'Dinosaur', 'Thunder', 'Illusion', 'Divine-Beast']), 'race'].unique())}")

        with display_count_archetype:
            st.markdown(f"**#Archetypes:** \n {len(st.session_state['data']['archetype'].unique())-1}")

        with display_count_staple:
            st.markdown(f"**#Staples:** \n {(st.session_state['data']['staple'] == 1).sum()}")

        with display_count_is_pendulum:
            st.markdown(f"**#Pendulum Monsters:** \n {(st.session_state['data']['is_pendulum'] == 1).sum()}")


    #####################################
    ######## FILTERING ##################
    #####################################

    col_filters, col_df = st.columns(2)

    with col_filters:

        # Filter einbauen
        st.subheader('Choose your filters', divider=True)

        # Input per Text Filtern
        if 'text_input' not in st.session_state:
            st.session_state['text_input'] = ''

        st.session_state['text_input'] = st.text_input("Filter by card name:", help="Search if your input text is in a card name and display those.", placeholder='Text to search for')


        # Nach Kartentyp Filtern
        if 'frameType_search' not in st.session_state:
            st.session_state['frameType_search'] = []

        options = [option.capitalize() for option in st.session_state['data']['frameType'].unique()]
        st.session_state['frameType_search'] = st.multiselect(label='Filter by card type', options=options, help='Filter for card types based on their border')
        st.session_state['frameType_search'] = [option.lower() for option in st.session_state['frameType_search']]

        # Nach Race filtern
        if 'race_search' not in st.session_state:
            st.session_state['race_search'] = []

        st.session_state['race_search'] = st.multiselect(
            label='Filter by type/race', 
            options=st.session_state['data']['race'].unique(), 
            help='Filter for types, e.g. "Continuous" or "Field"'
        )


        # Nach Attribute filtern
        if 'attribute_search' not in st.session_state:
            st.session_state['attribute_search'] = []

        st.session_state['attribute_search'] = st.multiselect(
            label='Filter by attribute', 
            options=st.session_state['data']['attribute'].unique(), 
            help='Filter for attributes, e.g. "FIRE"'
        )

        # nach archetype filtern
        if 'archetype_search' not in st.session_state:
            st.session_state['archetype_search'] = []

        st.session_state['archetype_search'] = st.multiselect(
            label='Filter by archetype', 
            options = st.session_state['data']['archetype'].unique(), 
            help='Filter for archetypes, e.g. "Alien".'
        )

        # nach atk filtern
        if 'atk_search' not in st.session_state:
            st.session_state['atk_search'] = 0

        st.session_state['atk_search'] = st.slider(
            label='Filter by attack',
            value=(-50.0, 6000.0),
            step=(50.0),
            help='Filter for atk".'
        )

        # Nach def filtern
        if 'def_search' not in st.session_state:
            st.session_state['def_search'] = 0

        st.session_state['def_search'] = st.slider(
            label='Filter by defense',
            value=(-50.0, 6000.0),
            step=(50.0),
            help='Filter for defense".'
        )


        # nach level filtern
        if 'level_search' not in st.session_state:
            st.session_state['level_search'] = 0

        st.session_state['level_search'] = st.slider(
            label='Filter by level',
            value=(-1.0, 14.0),
            step=(1.0),
            help='Filter for level".'
        )

        # nach scale filtern
        if 'scale_search' not in st.session_state:
            st.session_state['scale_search'] = 0

        st.session_state['scale_search'] = st.slider(
            label='Filter by scale',
            value=(-1.0, 14.0),
            step=(1.0),
            help='Filter for scale".'
        )

        # nach link rating filtern
        if 'linkval_search' not in st.session_state:
            st.session_state['linkval_search'] = 0

        st.session_state['linkval_search'] = st.slider(
            label='Filter by link rating',
            value=(0.0, 6.0),
            step=(1.0),
            help='Filter for link rating".'
        )

        # Auswahl Staple or not
        if 'staple_search' not in st.session_state:
            st.session_state['staple_search'] = False

        st.session_state['staple_search'] = st.toggle(
            label='Display Staples',
            help='If activated, only cards considered staples are displayed'
        )
        # Auswahl Pendulum or not
        if 'pendulum_search' not in st.session_state:
            st.session_state['pendulum_search'] = False

        st.session_state['pendulum_search'] = st.toggle(
            label='Display Pendulum Monsters',
            help='If activated, only Pendulum Monsters are displayed'
        )

    ###################################################
    ################## SHOW DATAFRAME #################
    ###################################################

    ########## Variables ##########

    # Werte aus st.session_state holen
    name = st.session_state.get('text_input', '')
    frameType = st.session_state.get('frameType_search', [])
    race = st.session_state.get('race_search', [])
    attribute = st.session_state.get('attribute_search', [])
    archetype = st.session_state.get('archetype_search', [])
    atk = st.session_state.get('atk_search', (0.0, 6000.0))
    defense = st.session_state.get('def_search', (0.0, 6000.0))
    level = st.session_state.get('level_search', (0.0, 14.0))
    scale = st.session_state.get('scale_search', (0.0, 14.0))
    linkval = st.session_state.get('linkval_search', (0.0, 6.0))
    staple = st.session_state.get('staple_search', False)
    pendulum = st.session_state.get('pendulum_search', False)

    ################ ANWENDEN ###############



    # Filter anwenden
    filtered_df = st.session_state['data']
    filtered_df['Show Card'] = False
    sc_beginning = ['Show Card'] + [col for col in filtered_df.columns if col != 'Show Card']
    filtered_df = filtered_df[sc_beginning]

    # Filter für 'name' (falls Text eingegeben wurde)
    if name:
        filtered_df = filtered_df[filtered_df['name'].str.contains(name, case=False, na=False)]

    # Filter für 'frameType' (falls eine Auswahl getroffen wurde)
    if frameType:
        filtered_df = filtered_df[filtered_df['frameType'].isin(frameType)]

    # Filter für 'race' (falls eine Auswahl getroffen wurde)
    if race:
        filtered_df = filtered_df[filtered_df['race'].isin(race)]

    # Filter für 'attribute' (falls eine Auswahl getroffen wurde)
    if attribute:
        filtered_df = filtered_df[filtered_df['attribute'].isin(attribute)]

    # Filter für 'archetype' (falls eine Auswahl getroffen wurde)
    if archetype:
        filtered_df = filtered_df[filtered_df['archetype'].isin(archetype)]

    # Filter für 'atk' (falls ein Bereich festgelegt wurde)
    if atk:
        filtered_df = filtered_df[(filtered_df['atk'] >= atk[0]) & (filtered_df['atk'] <= atk[1])]

    # Filter für 'defense' (falls ein Bereich festgelegt wurde)
    if defense:
        filtered_df = filtered_df[(filtered_df['def'] >= defense[0]) & (filtered_df['def'] <= defense[1])]

    # Filter für 'level' (falls ein Bereich festgelegt wurde)
    if level:
        filtered_df = filtered_df[(filtered_df['level'] >= level[0]) & (filtered_df['level'] <= level[1])]

    # Filter für 'scale' (falls ein Bereich festgelegt wurde)
    if scale:
        filtered_df = filtered_df[(filtered_df['scale'] >= scale[0]) & (filtered_df['scale'] <= scale[1])]

    # Filter für 'linkval' (falls ein Bereich festgelegt wurde)
    if linkval:
        filtered_df = filtered_df[(filtered_df['linkval'] >= linkval[0]) & (filtered_df['linkval'] <= linkval[1])]

    # Filter für 'staple' (falls eine Auswahl getroffen wurde)
    if staple:
        filtered_df = filtered_df[filtered_df['staple'] == True]

    # Filter für 'pendulum' (falls eine Auswahl getroffen wurde)
    if pendulum:
        filtered_df = filtered_df[filtered_df['is_pendulum'] == True]

    #Nachtraeglich die Ausgabe schoener machen insbesondere fuer Zauber & Fallen
    #filtered_df['atk'] = filtered_df['atk'].replace(-1, pd.NA)
    #filtered_df['def'] = filtered_df['def'].replace(-1, pd.NA)
    #filtered_df['linkval'] = filtered_df['linkval'].replace(0, pd.NA)
    #filtered_df['scale'] = filtered_df['scale'].replace(-1, 'None')
    #filtered_df['level'] = filtered_df['level'].replace(-1, 'None')
    #filtered_df['attribute'] = filtered_df['attribute'].replace('None', pd.NA)
    #filtered_df['archetype'] = filtered_df['archetype'].replace('None', pd.NA)


    with col_df:
        # Anzahl der findings ausgeben
        st.markdown(f'**Found cards:** {filtered_df.shape[0]}')

        # Dataframe mit Checkboxen
        edited_data = st.data_editor(
            filtered_df[['Show Card', 'name']],
            column_config={'Show Card':st.column_config.CheckboxColumn('Show Card')},
            hide_index=True,
            height=1000,
            use_container_width=True,
            disabled=filtered_df.drop(columns=['Show Card'], axis=1).columns
        )

    ###################################################
    ################## SHOW SELECTED CARDS ############
    ###################################################

    # Zeige die ausgewählten Karten basierend auf 'Show Card'
    selected_data = filtered_df[edited_data['Show Card'] == True]


    if not selected_data.empty:
        #Merge selected data with image links
        selected_image_df = pd.merge(selected_data, image_links, on='name', how='inner')
        container1 = st.container(height=600, border=False)

        with container1:
            for _, card in selected_image_df.iterrows():
                container = st.container(border=True)

                with container:
                    col_picture, col_stats1, col_stats2 = st.columns(3)

                    with col_picture:
                            st.image(card['card_image'], width=250)

                    with col_stats1: #hier alles effect related, kosmetisch in col_stats2

                        st.subheader('Game Attributes', divider=True)
                        st.write(f"**Name:** {card['name']}")
                        st.markdown(
                            f"**(Effect) Text:** <br>{card['desc']}",
                            unsafe_allow_html=True
                            )
                        st.write(f"**Card Type:** {card['frameType'].capitalize()}")

                        if card['level'] not in [-1,0]:
                            st.write(f"**Level/Rank:** {int(card['level'])}")

                        if card['attribute'] != 'None':
                            st.write(f"**Attribute:** {card['attribute']}")

                        st.write(f"**(Sub)type:** {card['race']}")

                        if int(card['linkval']) != 0:
                            st.write(f"**Link Rating:** {int(card['linkval'])}")

                        if int(card['scale']) != -1:
                            st.write(f"**Scale:** {int(card['scale'])}")

                        if int(card['atk']) != -1:
                            st.write(f"**Attack:** {int(card['atk'])}")

                        if int(card['def']) != -1:
                            st.write(f"**Defense:** {int(card['def'])}")

                        if card['archetype'] != 'None':
                            st.write(f"**Archetype:** {card['archetype']}")

                    ### Kosmetische Spalte
                    with col_stats2:
                        st.subheader('Other Attributes', divider=True)
                        st.write(f"**ID:** {int(card['id'])}")
                        st.write(f"**TCG-Release Date:** {card['tcg_date'].strftime('%Y-%m-%d')}")

                        st.subheader('YGOProDeck stats', divider=True)
                        if card['staple'] == 1:
                            st.write(f"**Considered Staple:** Yes")
                        else:
                            st.write(f"**Considered Staple:** No")

                        st.write(f"**Total Views:** {card['views']}")
                        st.write(f"**Total Upvotes:** {card['up_votes']}")
                        st.write(f"**Total Downvotes:** {card['down_votes']}")
                        st.write(f"**Cardmarket Price:** {card['card_price']} €")

                st.session_state['similar_cards'] = st.button('See similar cards', help='By pressing the button, a  machine learning algorithm will suggest similar cards to this card you have  selected.', key=card['name'])

                if st.session_state['similar_cards']:
                    con_sim_cards = st.container()
                    with con_sim_cards:
                        sim_cards = model2.find_similar_cards(data, card['name'])
                        sim_cards_w_images = pd.merge(sim_cards, image_links, on='name', how='inner')
                        image_columns = st.columns(5)
                        for found_card, col in zip(sim_cards_w_images.itertuples(), image_columns):
                            with col:
                                st.image(found_card.card_image)
                    # Zeige erweiterte Informationen an
                                with st.expander('More Details'):
                                    # Hole die Details zu dieser Karte aus dem DataFrame
                                    found_card_data = st.session_state['data'][st.session_state['data']['name'] == found_card.name]

                                    # Falls die Karte gefunden wurde, zeige die Details
                                    if not found_card_data.empty:
                                        st.write(f"**Name:** {found_card_data['name'].values[0]}")
                                        st.markdown(
                                            f"**(Effect) Text:** <br>{found_card_data['desc'].values[0]}",
                                            unsafe_allow_html=True
                                        )
                                        st.write(f"**Card Type:** {found_card_data['frameType'].values[0].capitalize()}")

                                        # Zeige Level/Rank nur, wenn vorhanden
                                        if found_card_data['level'].values[0] not in [-1, 0]:
                                            st.write(f"**Level/Rank:** {int(found_card_data['level'].values[0])}")

                                        # Zeige Attribut nur, wenn es nicht 'None' ist
                                        if found_card_data['attribute'].values[0] != 'None':
                                            st.write(f"**Attribute:** {found_card_data['attribute'].values[0]}")

                                        # Zeige (Sub)type
                                        st.write(f"**(Sub)type:** {found_card_data['race'].values[0]}")

                                        # Zeige Link Rating nur, wenn vorhanden
                                        if int(found_card_data['linkval'].values[0]) != 0:
                                            st.write(f"**Link Rating:** {int(found_card_data['linkval'].values[0])}")

                                        # Zeige Scale nur, wenn vorhanden
                                        if int(found_card_data['scale'].values[0]) != -1:
                                            st.write(f"**Scale:** {int(found_card_data['scale'].values[0])}")

                                        # Zeige Angriff, wenn vorhanden
                                        if int(found_card_data['atk'].values[0]) != -1:
                                            st.write(f"**Attack:** {int(found_card_data['atk'].values[0])}")

                                        # Zeige Verteidigung, wenn vorhanden
                                        if int(found_card_data['def'].values[0]) != -1:
                                            st.write(f"**Defense:** {int(found_card_data['def'].values[0])}")

                                        # Zeige Archetype, wenn vorhanden
                                        if found_card_data['archetype'].values[0] != 'None':
                                            st.write(f"**Archetype:** {found_card_data['archetype'].values[0]}")


    else:
        st.write('No cards selected')
