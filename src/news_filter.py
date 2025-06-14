# from news_classifier_load import classifier
import pandas as pd

from news_classifier_load import NewsClassifierLoader

classifier = NewsClassifierLoader("./models/logistic_regression_model.joblib")


def get_filtered_news(
    news_list,
    categories,
    choosen_categories,
):
    news_df = pd.DataFrame(news_list, columns=["text"])
    interesting_categories = [
        category_code
        for category, category_code in categories.items()
        if choosen_categories[category]
    ]

    news_classified = classifier.predict(news_df).tolist()

    news_interesting_list = [
        news
        for i, news in enumerate(news_list)
        if news_classified[i] in interesting_categories
    ]

    return news_interesting_list
