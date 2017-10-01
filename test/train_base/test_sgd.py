import unittest

from model.data import DataHandlerSingle
from model.training import TrainingBundle

from sklearn.linear_model import SGDClassifier
import numpy as np

class TestSGD(unittest.TestCase):

    def setUp(self):
        alg = SGDClassifier(loss='squared_hinge', alpha=1e-3, max_iter=50, tol=None)

        params = {
                'onevsrestclassifier__estimator__loss': ['squared_hinge'],
                'onevsrestclassifier__estimator__max_iter': [50],
                'onevsrestclassifier__estimator__alpha': (0.0001),
                'onevsrestclassifier__estimator__penalty': ('l2'), 
                'countvectorizer__ngram_range': [(1, 3)]
        }
        self.bundle = TrainingBundle('sgd', alg, params, nfolds = 2, n_jobs = 40)


    def test_reproduces_initial_results(self):
        X, y = DataHandlerSingle.load_data()

        print('Starting analysis ...')
        print('Data size', len(y), '\n\n')

        self.bundle.train_model(X, y)

 