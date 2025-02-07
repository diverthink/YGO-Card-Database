import numpy as np
import pandas as pd


def change_null_to_nan(df):
    data = df
    data.replace('null', np.nan, inplace = True)
    
    return data

def split_images(df, images=True, only_images=False):
    '''
    Splits the 'image' column from the original df and adds the 'names' column as a key if wished (default), otherwise it just drops the 'image' column. Don't forget to assign to two variables if images = True. You can also choose to export only an images DataFrame
    Params: DataFrame containing 'image' column, Optional: images=True (default), only_images=False (default)
    Returns: DataFrame without 'image' column and 'image' column DataFrame with columns 'name' and 'image' (default), if images = False, returns df with dropped 'image' column. If only_images = True, only the image DataFrame is returned.
    '''
    data = df

    if images:
        images_new = data[['card_image','name']]

    data_non_image = data.drop(columns=['card_image'], axis=1)
    
    if images == True:
        return data_non_image, images_new
    
    if only_images == True:
        return images_new
    
    return data_non_image


def drop_ocg(df):
    '''
    Drops cards that only have OCG printings.
    Params: DataFrame containing the card data and tcg_release
    Returns: DataFrame with only tcg released cards
    '''
    data = df
    data.dropna(subset="tcg_date", inplace=True)

    return data 
def drop_skillcards(df):
    '''
    Drops Speed Duel skill cards.
    Params: DataFrame containing the card data and card types.
    Returns: DataFrame without skill cards
    '''
    data = df
    data = data[data['type'] != "Skill Card"]

    return data
def drop_token(df):
    '''
    Drops Token Cards.
    Params: DataFrame containing the card data and card types.
    Returns: DataFrame without Token cards
    '''
    data = df
    data = data[data['type'] != "Token"]

    return data

def adapt_spell_trap(df):
    '''
    Changes 'atk', 'def', 'level' values of spells and traps to -1, since this is a value that does not exist in game and they should not have these values in the first place.
    Params: DataFrame containing the card data and card types.
    Returns: DataFrame without changed atk/def for spells and traps.
    '''
    data = df
    data.loc[data['type'].isin(['Spell Card', 'Trap Card']), ['atk', 'def', 'level']] = data.loc[data['type'].isin(['Spell Card', 'Trap Card']), ['atk', 'def', 'level']].fillna(-1) # change numeric values
    


    return data
def adapt_link_related(df):
    '''
    Adapts everything related to links and link monsters. Changes the level of a linkmonster to 0, sets linkval for everyother card to 0 (which can not be in the game, so indicating that its different). 'def' of linkmonsters set to 0 (as they count as 0 in game per definition).
    Params: DataFrame containing the card data and card types.
    Returns: DataFrame with 'level', 'def' = 0 for 'Link Monsters' 
            'linkval' = 0 for non-link monster.
    '''

    data = df
    data.loc[data['type'] == 'Link Monster', ['level', 'def']] = 0
    data.loc[data['type'] != 'Link Monster', ['linkval']] = 0

    return data

def adapt_pendulum(df):
    '''
    Changes scales for non-pendulum monsters and spell/trap cards to -1 indicating they have none, since -1 is a non existent scale in game.
    Params: DataFrame containing the card data and card types.
    Returns: DataFrame with 'scale' = -1 for non Pendulum Monsters.
    '''

    data = df
    data.loc[data['is_pendulum'] != 1, 'scale'] = -1

    return data

def na_attribute_archetype(df, attribute = True, archetype = True):
    '''
    Fills missing attribute and/or archetype values with 'None'
    Params: DataFrame containing the card data, attribute = True (default), archetype = True (default)
    Returns: DataFrame with 'None' where attribute and archetype are non-existent
    '''
    data = df

    if attribute:
        data['attribute'] = data['attribute'].fillna('None')
    
    if archetype:
        data['archetype'] = data['archetype'].fillna('None')

    return data
def staples(df):
    '''
    Assigns '0' in 'staple', if card is not considered staple.
    Params: DataFrame containing the card data
    Returns: DataFrame with '0', where 'staple' = NaN
    '''
    data = df

    data['staple'] = data['staple'].fillna(0)

    return data

def correct_dates(df):
    data = df
    data["tcg_date"] = pd.to_datetime(data["tcg_date"])

    return data


# Wir fuegen die Pendelmonster mit dem Rahmen zu ihrem Main Type hinzu und fuehren dann Pendulums nochmal gesondert auf.
def _pendulum(x):
    if 'pendulum' in x:
        return 1
    else:
        return 0


def _strip_pendulum(x):
    if '_pendulum' in x:
        return x.replace('_pendulum', '')
    else:
        return x


def pend_column(df):
    data = df
    data['is_pendulum'] = data['frameType'].apply(_pendulum)
    return data

def pend_into_maintype(df):
    data = df
    data['frameType'] = data['frameType'].apply(_strip_pendulum)
    return data
    
def wholesome_cleaning(df):
    '''
    Cleans the whole Yu-Gi-Oh Cards Dataframe with default settings of subfunctions.
    Params: DataFrame containing the card data.
    Returns: DataFrame with cleaned card data and DataFrame containing the image-links with card names.
    '''

    data_raw = df


    data = change_null_to_nan(data_raw)
    data, images = split_images(data)
    data = drop_ocg(data)
    data = drop_skillcards(data)
    data = drop_token(data)
    data = adapt_spell_trap(data)
    data = na_attribute_archetype(data)
    data = staples(data)
    data = correct_dates(data)

    data = pend_column(data)
    data = pend_into_maintype(data) 


    data = adapt_link_related(data)
    data = adapt_pendulum(data)
    
    return data, images


def save_data(df=None, image_df=None):
    
    if df is not None:
        df.to_csv("data/cards_cleaned.csv", index=False, sep="|")

    if image_df is not None:
        image_df.to_csv("data/image_links.csv", index=False, sep="|")

    return None



