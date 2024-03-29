import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline, Pipeline

from model.data import DataHandler
from model.multiple_outputs import MultipleOutputClassifier
from sklearn import metrics


def model_definition_words(threshold=0.05):
    est = make_pipeline(
        CountVectorizer(min_df=100, binary=True, analyzer='word'),
        MultipleOutputClassifier(
            base_estimator=RandomForestClassifier(n_estimators=100, min_samples_leaf=20, min_samples_split=40,
                                                  n_jobs=1, random_state = 1),
            threshold=threshold)
    )
    return est

def validate_model(X, y, pipeline_executable = model_definition_words):
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, random_state=1)
    X_trf, y_trf = DataHandler.flatten_data(X_tr, y_tr)

    est = pipeline_executable(0.05)
    est.fit(X_trf, y_trf)

    best_thres = 0
    best_mean_f1 = 0

    all_f1 = []
    for thres in [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10]:
        est.steps[-1][1].threshold = thres
        preds = est.predict(X_te)
        mean_f1 = f1_mean(y_te, preds) 
        
        # for yy, pp in zip(y_te[0:10], preds[0:10]):
            # print ('test', yy, 'predicted', pp)

        all_f1.append(mean_f1)
        if mean_f1 > best_mean_f1:
            best_thres = thres
            best_mean_f1 = mean_f1
        print('Thres {} avg f1 {}'.format(thres, mean_f1))
    print('Best threshold found {}'.format(best_thres))
    print('Best F1 {}'.format(best_mean_f1))
    # return best_thres
    return all_f1


def validate_model_multiclass(estimator, X, y, y_transformer = lambda x: x):
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, random_state=1)
    estimator.fit(X_tr, y_tr)
    test_predictions = estimator.predict(X_te)
    print('On test sample F1:', metrics.f1_score(y_te, test_predictions, average = 'micro'))

    y_te, test_predictions = y_transformer(y_te), y_transformer(test_predictions)
    print('Using custom F1 measure', f1_mean(y_te, test_predictions))

    # for true, test in zip(y_te[0:10], test_predictions[0:10]):
        # print('True {0} predicted {1}'.format(true, test))

def f1_mean(y_te, preds):
    f1_scores = np.array([f1(true, pred) for true, pred in zip(y_te, preds)]).mean()
    return f1_scores.mean()


def f1(true, pred):
    if len(pred) == 0:
        return 0
    tp = len(set(true).intersection(set(pred)))
    precision = tp / len(pred)
    recall = tp / len(true)

    if (precision + recall) == 0:
        return 0
    return (2 * precision * recall / (precision + recall))