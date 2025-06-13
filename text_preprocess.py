import pandas as pd
from sklearn.manifold import TSNE
import re
import nltk
from tqdm import tqdm
import nltk
from nltk.corpus import stopwords
import pymorphy3
from joblib import load

def tokenize(text):
    reg = re.compile(r'\w+')
    return reg.findall(text)

def stop_words_ret(): # выбираем какие стоп-слова будем удалять
    nltk.download('stopwords')
    stop_words = stopwords.words('russian')
    stop_words += ['фото', 'com', 'ru']
    return stop_words

def remove_stopwords(tokenized_texts): # удаляем
    clear_texts = []
    stop_words = stop_words_ret()
    for words in tokenized_texts:
        clear_texts.append([word for word in words if word not in stop_words])

    return clear_texts

def lemmatize_text(tokenized_texts): # нормализуем слова
    lemmatized_data = []
    lemmatizer = pymorphy3.MorphAnalyzer()
    for i, words in enumerate(tqdm(tokenized_texts)):
        lemmatized_words = [lemmatizer.normal_forms(word)[0] for word in words]
        lemmatized_data.append(lemmatized_words)
    return lemmatized_data

def identity_tokenizer(text): # надо для токенайзера
    return text

loaded_lr, loaded_vectorizer = load('logistic_regression_model.joblib') # грузим модель

dataset = pd.read_csv('X_test.csv')
dataset = dataset.head(10) # просто X_test слишком большой, там 80к строк
dataset = [tokenize(t.lower()) for t in dataset['text']] # токенизируем

dataset = remove_stopwords(dataset) # удаляем стоп-слова
lemmatized_dataset = lemmatize_text(dataset) # приводим в нормальную форму
tfidf_lemmatized_dataset = loaded_vectorizer.transform(lemmatized_dataset) # это tfidf векторайзер уже обученный
y_pred = loaded_lr.predict(tfidf_lemmatized_dataset)
print(y_pred)
