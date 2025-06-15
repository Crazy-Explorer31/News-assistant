import pandas as pd
from scipy import sparse
import requests
import joblib

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
from sklearn.svm import LinearSVC

model = LinearSVC(
    dual=False,
    penalty='l2',
    tol=1e-5,
    C=0.7,
    max_iter=20_000,
    class_weight='balanced',
    random_state=42
)

model.fit(tfidf_train, y_train)

y_pred_train = model.predict(tfidf_train)
accuracy = accuracy_score(y_train, y_pred_train)
print("Точность на тренировочной выборке:", accuracy)

y_pred = model.predict(tfidf_test)
accuracy = accuracy_score(y_test, y_pred)
print("Точность на тестовой выборке:", accuracy)

# joblib.dump(model, "../models/linear_svc_model.joblib") # need to add vectorizer
