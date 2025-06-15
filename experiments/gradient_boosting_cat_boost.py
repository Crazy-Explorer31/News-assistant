import pandas as pd
from scipy import sparse
import requests

tfidf_train = sparse.load_npz("tfidf_train_sparse.npz")
tfidf_test = sparse.load_npz("tfidf_test_sparse.npz")

datasets = {

  "y_test.csv" : "https://www.dropbox.com/scl/fi/3c7br6x2k0lo6iujtwzt0/y_test.csv?rlkey=9rlywjvoduahpu27uoclmmtqg&st=5hyfuf7b&dl=1",

  "y_train.csv" : "https://www.dropbox.com/scl/fi/n228uag3g0qqdigwlu151/y_train.csv?rlkey=8g2nm1w539t7o84k8jceqfdtz&st=tskbwl6g&dl=1",

  "X_train.csv" : "https://www.dropbox.com/scl/fi/eraukmu5w1r56vigj1bla/X_train.csv?rlkey=gpzrwnvhhk6q07r9nklz09fl1&st=vnux3ves&dl=1",

  "X_test" : "https://www.dropbox.com/scl/fi/a4dlgfke5swfjkolikr5o/X_test.csv?rlkey=2u02d3zmy0ls59katzrwljpgq&st=w6w9egec&dl=1"
}

def get_dataset(url, dataset_name):
    response = requests.get(url)

    with open(dataset_name, 'wb') as file:
        file.write(response.content)

    df = pd.read_csv(dataset_name)
    return df

y_train = get_dataset(datasets['y_train.csv'], 'y_train.csv')['category']
y_test = get_dataset(datasets['y_test.csv'], 'y_test.csv')['category']

from sklearn.metrics import accuracy_score
from catboost import CatBoostClassifier
import joblib

cat_boost = CatBoostClassifier(
    iterations=500,
    learning_rate=0.1,
    depth=8,
    loss_function='MultiClass',
    devices=':0',
    verbose=10,
    early_stopping_rounds=50,
    bootstrap_type='Bayesian',
    used_ram_limit='10gb',
)


cat_boost.fit(tfidf_train, y_train)

y_pred_train = cat_boost.predict(tfidf_train)
accuracy = accuracy_score(y_train, y_pred_train)
print("Точность на тренировочной выборке:", accuracy)

y_pred = cat_boost.predict(tfidf_test)
accuracy = accuracy_score(y_test, y_pred)
print("Точность на тестовой выборке:", accuracy)

# joblib.dump(cat_boost, "../models/catboost_model.joblib") # need to add vectorizer
