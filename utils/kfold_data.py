import os
import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold, KFold


def generate_data(random_state=666, dataset=None, date=None):
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=random_state)

    for fold, (train_index, dev_index) in enumerate(skf.split(X, y)):
        print(fold, "TRAIN:", train_index, "TEST:", dev_index)
        DATA_DIR = "./data/data_StratifiedKFold_{}_{}/{}/data_fold_{}/".format(random_state, date, dataset, fold)
        # DATA_DIR = "./data/transdata_StratifiedKFold_{}/{}/data_fold_{}/".format(random_state, dataset, fold)
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        tmp_train_df = train_df.iloc[train_index]
        tmp_dev_df = train_df.iloc[dev_index]
            
        tmp_train_df.to_csv(DATA_DIR + "/train.csv", index=False, header=False, sep='\t', encoding='utf-8')
        tmp_dev_df.to_csv(DATA_DIR + "/test.csv", index=False, header=False, sep='\t', encoding='utf-8')
        print(tmp_train_df.shape, tmp_dev_df.shape)


if __name__=="__main__":
    dataset = 'cn'
    date = '0813'
    # path = './data/pseudo_{}/{}_total_pseudo.csv'.format(date, dataset)
    # path =  './data/transform/{}_total.csv'.format(dataset)
    train_df = pd.read_csv('data/pseudo_0726/cn_total_pseudo.csv', encoding='utf-8')
    # train_df = pd.read_csv(path, encoding='utf-8')
    train_df = train_df[['Dialogue_id', 'Speaker', 'Sentence', 'Label']]
    # train_df = train_df[['Dialogue_id', 'Speaker1', 'Speaker2', 'Sentence1', 'Sentence2', 'Label']]
    X = np.array(train_df.index)
    y = train_df.loc[:, 'Label'].to_numpy()

    generate_data(random_state=666, dataset=dataset, date=date)