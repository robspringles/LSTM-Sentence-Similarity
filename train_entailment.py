from random import shuffle

import pickle
import numpy as np
from sklearn.svm import SVC

from lstm import lstm
from util_files.Constants import data_folder, use_noise, models_folder
from util_files.data_utils import prepare_sent_pairs_data, get_discrete_accuracy



def prepare_entailment_data(data):
    return map(lambda entry: [entry[0], entry[1], entry[3]], data)

def prepare_svm_train_data(mydata, lst):
    # type: (list, lstm) -> tuple
    num = len(mydata)
    features = []
    ys = []
    use_noise.set_value(0.)

    for idx in range(0, num):  # I don't use batches to make calculating each feature vector easier
        [sent1, sent2, y] = mydata[idx]
        emb1 = lst.get_sentence_embedding(sent1)
        emb2 = lst.get_sentence_embedding(sent2)
        feat_vect = np.append(np.fabs(emb1-emb2), [emb1*emb2])  # as described in the orig paper
        ys.append(y)
        features.append(feat_vect)

    features = np.array(features)
    ys = np.array(ys)
    return features, ys

model_name = "negative_5000_model.p"
# lst=lstm(models_folder + "bestsem.p",load=True,training=False)
lst = lstm.load_from_pickle(models_folder + model_name)
train = pickle.load(open(data_folder + "semtrain.p", 'rb'))
train = prepare_entailment_data(train)

shuffle(train)
xdat, ydat = prepare_svm_train_data(train, lst)
train_lim = int(0.7 * len(xdat))

x_train = xdat[0:train_lim]
y_train = ydat[0:train_lim]
x_cross_val = xdat[train_lim:]
y_cross_val = ydat[train_lim:]

clf = SVC(C=100, gamma=3.1, kernel='rbf')
clf.fit(x_train, y_train)

print "Training accuracy:", get_discrete_accuracy(clf, x_train, y_train)
print "Cross validation accuracy:", get_discrete_accuracy(clf, x_cross_val, y_cross_val)
