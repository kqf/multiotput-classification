import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline, Pipeline

from multiple_outputs import MultipleOutputClassifier


def load_data():
    df_category_mapping = pd.read_csv('data/category_mapping.csv', sep='\t')
    category_mapping = dict(zip(df_category_mapping.raw, df_category_mapping.mapped))
    df = (pd.read_csv('data/categories.csv')
          .assign(categories=lambda x: x.categories.map(eval))
          .dropna()
          .loc[lambda x: x.categories.map(len) > 0])
    category_dict = [{cat: 1 for cat in cats} for cats in list(df.categories)]
    encoder = DictVectorizer()
    encoder.fit(category_dict)
    categories_mat = encoder.transform(category_dict)
    categories_counts = np.asarray(categories_mat.sum(0).reshape(-1), dtype=np.int)[0]
    categories_dist = dict(zip(encoder.feature_names_, categories_counts))
    df['most_popular_category'] = df.categories.map(
        lambda x: sorted(x, key=lambda x: categories_dist[x], reverse=True)[0])

    descriptions = df['short_description']
    categories = df['categories'].map(lambda x: [category_mapping[c] for c in x])

    return descriptions.values, categories.values


def flatten_data(X, Y):
    X_flat = []
    y_flat = []
    for x, ys in zip(X, Y):
        for y in ys:
            X_flat.append(x)
            y_flat.append(y)
    return X_flat, y_flat


def model_definition_words(threshold=0.05) -> Pipeline:
    est = make_pipeline(
        CountVectorizer(min_df=100, binary=True, analyzer='word'),
        MultipleOutputClassifier(
            base_estimator=RandomForestClassifier(n_estimators=100, min_samples_leaf=20, min_samples_split=40,
                                                  n_jobs=-2),
            threshold=threshold)
    )
    return est


def validate_model():
    print('Loading data')
    X, y = load_data()
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, random_state=1)
    X_tr_flat, y_tr_flat = flatten_data(X_tr, y_tr)

    est = model_definition_words(0.05)
    est.fit(X_tr_flat, y_tr_flat)

    best_thres = 0
    best_mean_f1 = 0

    for thres in [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10]:
        est.steps[-1][1].threshold = thres
        preds = est.predict(X_te)
        mean_f1 = np.array([f1(true, pred) for true, pred in zip(y_te, preds)]).mean()
        if mean_f1 > best_mean_f1:
            best_thres = thres
            best_mean_f1 = mean_f1
        print('Thres {} avg f1 {}'.format(thres, mean_f1))
    print('Best threshold found {}'.format(best_thres))
    print('Best F1 {}'.format(best_mean_f1))
    return best_thres


def f1(true, pred):
    if len(pred) == 0:
        return 0
    tp = len(set(true).intersection(set(pred)))
    precision = tp / len(pred)
    recall = tp / len(true)
    if (precision + recall) == 0:
        return 0
    else:
        return (2 * precision * recall / (precision + recall))


if __name__ == '__main__':
    best_thres = validate_model()
