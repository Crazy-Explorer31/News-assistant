import pandas as pd
from scipy import sparse
import requests
from sklearn.metrics import accuracy_score
from src.news_classifier_load import *
from sklearn.svm import LinearSVC
import ssl
import nltk

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('stopwords')

from joblib import load, dump
from src.news_classifier_load import NewsClassifierLoader


with open("../data/validation_posts.txt") as f:
    news_list = f.read().strip().split('@')

with open("../data/validation_answers.txt") as f:
    y_test = list(map(int, f.read().strip().split()))

news_df = pd.DataFrame(news_list, columns=["text"])

svc_model = NewsClassifierLoader("../models/linear_svc_clf_and_vec.joblib")
y_pred = svc_model.predict(news_df).tolist()
acc = accuracy_score(y_test, y_pred)
print(f"svc  accuracy: {acc}")

clf_svc = svc_model.classifier
vectorizer = svc_model.vectorizer
with open("../data/train_posts.txt") as f:
    news_train = f.read().strip().split('@')
with open("../data/train_answers.txt") as f:
    y_train = list(map(int, f.read().strip().split()))

df = pd.DataFrame()
df["text"] = news_train
preprocessed_dataset = get_preprocessed_dataset(df, vectorizer)
clf_svc.fit(preprocessed_dataset, y_train)
svc_model.classifier = clf_svc
y_pred = svc_model.predict(news_df).tolist()
acc = accuracy_score(y_test, y_pred)
print(f"new svc  accuracy: {acc}")

dump((clf_svc, vectorizer), '../models/svc_tuned_model_and_vec.joblib')
