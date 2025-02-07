import streamlit as st
import pandas as pd
import plotly.express as px

import model2


def app(data: pd.DataFrame, image_links: pd.DataFrame):
    
    # Get data
    df = data.copy()
    image_links = image_links.copy()


    # Set dtypes to the right types
    df = model2.adapt_dtypes(df)
    df['tcg_date'] = pd.to_datetime(df["tcg_date"]).dt.date
    df['tcg_year'] = pd.to_datetime(df['tcg_date']).dt.year.astype('object')
    df['card_price'] = df['card_price'].astype('float')
    df.drop(columns=['id'], axis=1, inplace=True)

    st.title("Visualise the YGO-Data!")


    # Settings
    cont_auswahl = st.container()
    with cont_auswahl:
        st.subheader("Visualisation Settings", divider=True)
        col1, col2 = st.columns(2,)    
        filters = {}
        
        with col1:
            
            chart_type = st.selectbox("Choose the Method", ["Scatterplot", "Barplot", "Boxplot"])
            category = st.selectbox("Group by (optional)", [None] + list(df[['type', 'race', 'attribute', 'archetype', 'frameType', 'staple', 'tcg_year']].columns))
        
        with col2:
            if chart_type == 'Scatterplot':
                choices = df[['up_votes', 'down_votes', 'views', 'atk', 'def', 'level', 'linkval', 'scale', 'card_price']].columns
                x_axis = st.selectbox("Choose x-axis", choices)
                y_axis = st.selectbox("Choose y-axis", choices)
            elif chart_type in ["Barplot", "Boxplot"]:
                choices_x = df[['type', 'race', 'attribute', 'archetype', 'frameType', 'staple', 'tcg_year']].columns
                choices_y = [None] + list(df[['up_votes', 'down_votes', 'views', 'atk', 'def', 'level', 'linkval', 'scale', 'card_price']].columns)
                x_axis = st.selectbox("Choose x-axis", choices_x)
                y_axis = st.selectbox("Choose y-axis", choices_y)
            
        # Filter Settings   
        cont_filter = st.container(border=True)
        # Categoric Filter:
        with cont_filter:

            col_cat, col_num = st.columns(2,)

            with col_cat:
                st.subheader('Categorical Filter', divider=True)
                for column in df[['type', 'race', 'attribute', 'archetype', 'frameType', 'staple', 'tcg_year']]:
                    unique_values = df[column].unique()
                    selected_values = st.multiselect(f"Filter: {column}", unique_values)
                    filters[column] = selected_values

        
    
        
        # Numeric Filter
            with col_num:
                st.subheader('Numeric Filter', divider=True)
                for column in ['atk', 'def', 'level', 'linkval', 'scale', 'card_price']: 
                    min_val, max_val = df[column].min(), df[column].max()
                    if min_val != max_val:
                        if df[column].dtype == 'int':
                            step = max((max_val - min_val) // 100, 1)
                            selected_range = st.slider(f"Filter: {column}", min_value=int(min_val), max_value=int(max_val), value=(int(min_val), int(max_val)), step=step)
                        elif df[column].dtype == 'float':
                            min_value = st.number_input(f'Filter: Min {column}', min_value=-1.0, max_value=max_val, value=min_val)
                            max_value = st.number_input(f'Filter: Max {column}', min_value=-1.0, max_value=max_val, value=max_val)
                            selected_range = (min_value, max_value)
                        filters[column] = selected_range
                
            

    df_filtered = df.copy()
    
    for column, values in filters.items():
        if isinstance(values, tuple):
            df_filtered = df_filtered[(df_filtered[column] >= values[0]) & (df_filtered[column] <= values[1])]
        elif values:
            df_filtered = df_filtered[df_filtered[column].isin(values)]                
    
    
    
    cont_figure = st.container()

    # Visualise it
    with cont_figure:
        st.subheader('Visualisation', divider=True)
        if chart_type == "Scatterplot":
            fig = px.scatter(df_filtered, x=x_axis, y=y_axis, color=category, title=f"Scatterplot: {y_axis} vs {x_axis}", hover_name=df_filtered['name'])
        elif chart_type == "Barplot":
            if y_axis != None:
                fig = px.histogram(df_filtered, x=x_axis, y=y_axis, color=category, barmode='group', histfunc='avg', title=f"Barplot: {y_axis} vs {x_axis}")
            else:
                fig = px.bar(df_filtered, x=x_axis, y=y_axis, color=category, title=f"Barplot: {y_axis} vs {x_axis}")
        #elif chart_type == "Liniendiagramm":
        #    fig = px.line(df_filtered, x=x_axis, y=y_axis, color=category, title=f"Liniendiagramm: {y_axis} vs {x_axis}")
        elif chart_type == "Boxplot":
            fig = px.box(df_filtered, x=x_axis, y=y_axis, color=category, title=f"Boxplot: {y_axis} vs {x_axis}")

        st.plotly_chart(fig)