import pandas as pd
import pickle
from kmodes.kmodes import KModes
import seaborn as sns
import matplotlib.pyplot as plt

def preprocessing(X):
    '''
    Features as input:
    - gamecategory
    - subgamecategory
    - bundle
    - created
    - shift
    - oblast
    - city
    - os
    - osv
    - hour_shift
    - local_time
    - month
    - date
    - day
    - wd
    - hour
    - minutes
    - Segment - output of classification model (1-5 segment numbers)
    '''
    X = X.copy()
    night = (X.hour >= 22) | (X.hour < 9)
    work = (X.hour >= 9) & (X.hour < 18)
    evening = (X.hour >= 18) & (X.hour < 22)

    X.hour[night] = 'night'
    X.hour[work] = 'work'
    X.hour[evening] = 'evening'

    X.os = X.os.str.lower()

    X.osv = X.osv.str.split('.').str[0]
    X['osv'] = X['os'] + X['osv']

    X['subgamecategory'] = X['gamecategory'] + '_' + X['subgamecategory']

    X.drop(['created',
            'shift',
            'bundle',
            'local_time',
            'city',
            'hour_shift',
            #         'month',
            'minutes',
            'day',
            'subgamecategory',
            'date'
            ], axis=1, inplace=True)

    # X.bundle = X.bundle.str.split('.').str[0]

    return X

def table_generation(X):
    NUMBER_OF_PLACES = 2

    dict_info = {}
    for cluster in range(X.cluster.nunique()):
        dict_ = {}
        for col in X.columns[:-1]:
            X_clustered = X[X.cluster == cluster]
            a = (X_clustered[col].value_counts() / len(X_clustered) * 100)[:NUMBER_OF_PLACES].to_dict()
            temp = [str(i)+f' ({str(round(j,1))}%)' for i,j in zip(a.keys(), a.values())]
            while len(temp) < NUMBER_OF_PLACES:
                temp += ['- (0%)']
            dict_[col] = temp
        dict_info[f'Кластер № {cluster}'] = pd.DataFrame(dict_, index=['Самый частый', 'Второе место'])

    return pd.concat(dict_info)


def model_inference(X):
    X = X.copy()
    if 'cluster' in X.columns:
        X = X.drop('cluster', axis=1)

    with open('clustering.pickle', 'rb') as f:
        kmode = pickle.load(f)

    clusters = kmode.predict(X)
    return clusters


if __name__ == '__main__':

    X = preprocessing(pd.read_csv('part_of_train_data.csv', index_col='Unnamed: 0'))

    X['cluster'] = model_inference(X)
    X.info()

    X = table_generation(X)
    X.info()
