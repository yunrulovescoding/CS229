from itertools import combinations

import pandas as pd
import numpy as np
import scipy.sparse as sp
from scipy.sparse import coo_matrix
from lightfm import LightFM
from sklearn.preprocessing import LabelEncoder
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

from kmodes.kmodes import KModes

train_X = pd.read_csv('new_data/new_train_X.csv')
val_X = pd.read_csv('new_data/new_valid_X.csv')
train_y = pd.read_csv('new_data/new_train_y.csv')
val_y = pd.read_csv('new_data/new_valid_y.csv')
test_X = pd.read_csv('new_data/new_test_X.csv')
test_y = pd.read_csv('new_data/new_test_y.csv')

train_X_all = pd.concat([train_X, val_X,test_X])

song_features = ['song_id','genre_ids', 'artist_name', 'composer', 'lyricist','language']
#user_features = ['msno','city', 'gender', 'registered_via']
ui_features = ['source_screen_name', 'source_system_tab', 'source_type']
cat_features = ['song_id','genre_ids', 'artist_name', 'composer', 'lyricist','language','msno','city', 'gender', 'registered_via',
               'source_screen_name', 'source_system_tab', 'source_type']

song_df = train_X_all[song_features].copy()
song_df.head()

km2 = KModes(n_clusters=200, init='Huang', n_init=5, verbose=1)
song_clusters = km2.fit_predict(song_df)

songc = pd.DataFrame(song_clusters)
songc.columns=['songc_cluster']
songc.head()

songc.to_csv('new_data/all_songc.csv',index=False)