import re

import nltk
import pandas as pd
import pymorphy3
from joblib import load
from nltk.corpus import stopwords
from tqdm import tqdm


def tokenize(text):
    reg = re.compile(r"\w+")
    return reg.findall(text)


def stop_words_ret():  # выбираем какие стоп-слова будем удалять
    nltk.download("stopwords")
    stop_words = stopwords.words("russian")
    stop_words += ["фото", "com", "ru"]
    return stop_words


def remove_stopwords(tokenized_texts):  # удаляем
    clear_texts = []
    stop_words = stop_words_ret()
    for words in tokenized_texts:
        clear_texts.append([word for word in words if word not in stop_words])

    return clear_texts


def lemmatize_text(tokenized_texts):  # нормализуем слова
    lemmatized_data = []
    lemmatizer = pymorphy3.MorphAnalyzer()
    for i, words in enumerate(tqdm(tokenized_texts)):
        lemmatized_words = [lemmatizer.normal_forms(word)[0] for word in words]
        lemmatized_data.append(lemmatized_words)
    return lemmatized_data


def identity_tokenizer(text):  # надо для токенайзера
    return text


def get_preprocessed_dataset(dataset, vectorizer):
    dataset = [tokenize(t.lower()) for t in dataset["text"]]  # токенизируем
    dataset = remove_stopwords(dataset)  # удаляем стоп-слова
    dataset = lemmatize_text(dataset)  # приводим в нормальную форму
    dataset = vectorizer.transform(dataset)  # это tfidf векторайзер уже обученный

    return dataset


class NewsClassifierLoader:
    def __init__(self, path_to_classifier):
        self.classifier, self.vectorizer = load(path_to_classifier)  # грузим модель

    def predict(self, dataset: pd.DataFrame):
        preprocessed_dataset = get_preprocessed_dataset(dataset, self.vectorizer)
        y_pred = self.classifier.predict(preprocessed_dataset)

        return y_pred


def run_example():
    dataset = pd.read_csv("X_test.csv")
    dataset = dataset.head(10)  # просто X_test слишком большой, там 80к строк

    clfr = NewsClassifierLoader("./models/logistic_regression_model.joblib")

    y_pred = clfr.predict(dataset)

    print(y_pred)
