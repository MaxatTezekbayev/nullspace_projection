"""
Usage:
  main.py [--input_dir=INPUT_DIR] [--output_dir=OUTPUT_DIR]

Options:
  -h --help                     show this help message and exit
  --input_dir=INPUT_DIR         input dir file
  --output_dir=OUTPUT_DIR       write down output file

Script for collecting potential verbs from the aspecutal verbs list.
"""

import numpy as np
from docopt import docopt
from sklearn.svm import LinearSVC
from sklearn.linear_model import SGDClassifier
from sklearn.utils import shuffle

from src import debias


def load_data(path):
    fnames = ["neg_neg.npy", "neg_pos.npy", "pos_neg.npy", "pos_pos.npy"]
    protected_labels = [0, 1, 0, 1]
    main_labels = [0, 0, 1, 1]
    X, Y_p, Y_m = [], [], []

    for fname, p_label, m_label in zip(fnames, protected_labels, main_labels):
        print(path + '/' + fname)
        data = np.load(path + '/' + fname)
        for x in data:
            X.append(x)
        for _ in data:
            Y_p.append(p_label)
        for _ in data:
            Y_m.append(m_label)

    Y_p = np.array(Y_p)
    Y_m = np.array(Y_m)
    X = np.array(X)
    X, Y_p, Y_m = shuffle(X, Y_p, Y_m, random_state=0)
    return X, Y_p, Y_m


def find_projection_matrices(X_train, Y_train_protected, X_dev, Y_dev_protected, dim, out_dir, Y_train_main, Y_dev_main):
    # num_clfs = [20, 50, 100]
    is_autoregressive = True
    min_acc = 0.
    noise = False

    # for n in num_clfs:
    n = 200
    print("num classifiers: {}".format(n))

    # clf = LinearSVC
    clf = SGDClassifier
    # params = {'max_iter': 2000, 'fit_intercept': True, 'class_weight': "balanced", 'dual': False}
    # params = {'max_iter': 2000, 'fit_intercept': True, 'penalty': "l2", 'n_jobs': 32}
    params = {'warm_start': True, 'loss': 'log', 'n_jobs': -1, 'max_iter': 200, 'random_state': 0, 'tol': 1e-3}

    P_n = debias.get_debiasing_projection(clf, params, n, dim, is_autoregressive, min_acc,
                                          X_train, Y_train_protected, X_dev, Y_dev_protected, noise=noise,
                                          by_class=True, Y_train_main=Y_train_main, Y_dev_main=Y_dev_main)
    fname = out_dir + "/P.num-clfs={}.npy".format(n)
    np.save(fname, P_n)


if __name__ == '__main__':
    arguments = docopt(__doc__)

    in_dir = arguments['--input_dir']

    out_dir = arguments['--output_dir']

    x_train, y_train_protected, y_train_main = load_data(in_dir + '/train/')
    x_dev, y_dev_protected, y_dev_main = load_data(in_dir + '/dev/')
    find_projection_matrices(x_train, y_train_protected, x_dev, y_dev_protected, 300, out_dir, y_train_main, y_dev_main)

