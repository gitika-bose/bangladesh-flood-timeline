import os
import pandas as pd
import json
from sklearn import model_selection

"""
type = m_6
newspaper = m_30
is_flood = m_28
flood_related = m_57
is_bangladesh = m_55
flood-climatechange = m_33
"""

def get_data_json(file, folder):
    filepath = os.path.join(folder, file)
    js = json.load(open(filepath))

    filename = js.get('filename',None)
    doc_id = None
    if filename:
        filename2 = filename.replace('.ann','').replace('.txt','').replace('.json','')
        if('_data_') in filename2:
            splt =  filename2.split('_data_')
            if len(splt)>1:
                doc_id = splt[1].replace('_', '-')

    text = js.get('text',None)

    is_flood, is_bangladesh, flood_related, flood_climatechange, newspaper, flood_type = \
        None, None, None, None, None, None
    if 'm_28' in js['metas']: is_flood = js['metas']['m_28']['value']
    if 'm_6' in js['metas']: flood_type = js['metas']['m_6']['value']
    if 'm_30' in js['metas']: newspaper = js['metas']['m_30']['value']
    if 'm_57' in js['metas']: flood_related = js['metas']['m_57']['value']
    if 'm_55' in js['metas']: is_bangladesh = js['metas']['m_55']['value']
    if 'm_33' in js['metas']: flood_climatechange = js['metas']['m_33']['value']

    return {
        'doc_id': doc_id,
        'filename': file,
        'text': text,
        'is_flood': is_flood,
        'is_bangladesh': is_bangladesh,
        'flood_related': flood_related,
        'flood_climatechange': flood_climatechange,
        'newspaper': newspaper,
        'flood_type': flood_type
    }


def load_data(data_folder='data', save_file=None):
    data_files = [f for f in os.listdir(data_folder) if '.json' in f]
    data = [get_data_json(f, data_folder) for f in data_files]

    columns = ['doc_id', 'filename', 'is_flood', 'is_bangladesh', 'flood_related', 'flood_climatechange', 'newspaper', 'flood_type', 'text']
    df = pd.DataFrame(data,columns=columns)
    if save_file: df.to_csv(save_file)
    return df


def query_dataframe(df, d):
    df2 = df.copy()
    for key, val in d.items(): df2 = df2.loc[df2[key] == val]
    return df2


def train_test_split(df, test_size=0.2, random_state=42): return model_selection.train_test_split(df, test_size=test_size, random_state=random_state)



if __name__=='__main__':
    df = load_data()
    train,test = train_test_split(df)
    # print(len(df.loc[df['is_flood']==True])
