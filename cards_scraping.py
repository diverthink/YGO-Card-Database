import pandas as pd
import requests
import json



def _get_all_card_info():
    '''
    Gets all infos about every card from the ygoprodeck api.

    Parameters:
        None

    Returns:
        Dictionary with every card in the game.

    '''

    url = 'https://db.ygoprodeck.com/api/v7/cardinfo.php?misc=yes'
    res = requests.get(url)
    
    if res.status_code == 200:
        all_cards_data = res.json()
    else:
        print(f'Something went wrong! Error Code: {res.status_code}')
        return None

    with open('card_infos.json', 'w') as file:
        json.dump(all_cards_data, file)

    return all_cards_data




def make_it_dataframe(all_cards_json=None):
    '''
    Strips the card_info_output to the necessary values.

    Parameters:
        all_cards_json (optional, default = None): a json file from the ygoprodeck api, containing card information. If not given _get_all_card_info as default.

    Returns:
        Pandas DataFrame with columns = id, name, type, desc, race, card_image, card_price, up_votes, down_votes, views. And the respectable cards as rows.
        if value was non existent in input 'null' is returned in row.
        
    '''
    if all_cards_json:
        all_cards = all_cards_json

    else:
        all_cards = _get_all_card_info()
    
    # Zunaechst alle Eigenschaften, die alle Karten haben
    make_dict = {'id': [card['id'] for card in all_cards['data']],
                 'name': [card['name'] for card in all_cards['data']],
                 'type': [card['type'] for card in all_cards['data']],
                 'desc': [card['desc'] for card in all_cards['data']],
                 'race': [card['race'] for card in all_cards['data']],
                 'card_image': [card['card_images'][0]['image_url'] for card in all_cards['data']],
                 'card_price': [card['card_prices'][0]['cardmarket_price'] for card in all_cards['data']],
                 'up_votes': [card['misc_info'][0]['upvotes'] for card in all_cards['data']],
                 'down_votes': [card['misc_info'][0]['downvotes'] for card in all_cards['data']],
                 'views': [card['misc_info'][0]['views'] for card in all_cards['data']]}
    
    # Jetzt alle, die nur die Monster betreffen
    atk = []
    defense = []
    level = []
    attribute = []
    archetype = []
    linkval = []
    scale = []
    tcg_date = []
    frameType = []

    # nochmal extra behandeln: 'archetype': [card['archetype'] for card in all_cards['data']]

    for card in all_cards['data']:
        if 'archetype' in card.keys():
            archetype.append(card['archetype'])
        else:
            archetype.append('null')

    for card in all_cards['data']:
        if 'atk' in card.keys():
            atk.append(card['atk'])
            defense.append(card['def'])
            level.append(card['level'])
            attribute.append(card['attribute'])
        
        else:
            atk.append('null')
            defense.append('null')
            level.append('null')
            attribute.append('null')

    for card in all_cards['data']:
        if 'linkval' in card.keys():
            linkval.append(card['linkval'])

        else:
            linkval.append('null')

    for card in all_cards['data']:
        if 'scale' in card.keys():
            scale.append(card['scale'])
        else:
            scale.append('null')


    for card in all_cards['data']:
        if 'tcg_date' in card['misc_info'][0].keys():
            tcg_date.append(card['misc_info'][0]['tcg_date'])
        else:
            tcg_date.append('null')

    for card in all_cards['data']:
        if 'frameType' in card.keys():
            frameType.append(card['frameType'])
        else:
            frameType.append('null')


    # in dictionary einfuegen
    make_dict['atk'] = atk
    make_dict['def'] = defense
    make_dict['level'] = level
    make_dict['attribute'] = attribute
    make_dict['archetype'] = archetype
    make_dict['linkval'] = linkval
    make_dict['scale'] = scale
    make_dict['tcg_date'] = tcg_date
    make_dict['frameType'] = frameType


    # Dataframe basteln

    df = pd.DataFrame(make_dict)

    return df


def extract_prices(card_infos):
    '''
    Only extracts the prices of the cards.
    
    Parameter: card_infos, a JSON from ygoprodeck api containing all card infos and their prices.
    
    Returns: a dictionary with 'id': 'price' per card.
    '''
    card_prices = {}

    for card in card_infos['data']:
        card_prices[f'{card["id"]}'] = card['card_prices'][0]['cardmarket_price']
    
    return card_prices


# Alle Karten scrapen, welche als staple gekennzeichnet sind und mit dem original df verbinden.

def get_staples(all_cards):
    '''
    Searches for cards marked as staples in the database and attaches the new column "staple" onto an existing dataframe.
    
    Parameter: card_infos, a Pandas Dataframe minimally containing card names.
    
    Returns: a DataFrame with the new column 'staple'. With 1 if it is a staple and NaN if it is not.
    '''

    url = 'https://db.ygoprodeck.com/api/v7/cardinfo.php?staple=yes'
    res = requests.get(url)
    
    if res.status_code == 200:
        staple_cards = res.json()
    else:
        print(f'Something went wrong! Error Code: {res.status_code}')
        return None
    
    staples = {}
    for card in staple_cards['data']:
        staples[f'{card["name"]}'] = 1
    
    all_cards['staple'] = all_cards['name'].map(staples)

    return all_cards


