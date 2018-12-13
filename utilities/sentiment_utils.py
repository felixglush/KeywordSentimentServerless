def return_fake_data(num_docs):
    return create_fake_data(num_docs)


def create_fake_data(num_of_posts):
    fake_data = {"ResultList": [], "ErrorList": []}
    for i in range(num_of_posts):
        fake_sentiment_item = {
            'Index': i,
            'Sentiment': 'placeholder sentiment',
            'SentimentScore': {
                'Positive': 0.0,
                'Negative': 0.0,
                'Neutral': 0.0,
                'Mixed': 0.0
            }
        }
        fake_data["ResultList"].append(fake_sentiment_item)
    return fake_data


# text sent to Amazon Comprehend must be under 5000 bytes
def is_text_within_limits(document):
    return 0 < len(document) <= 5000


def documents_within_limits(*text_list):
    for text in text_list:
        if not is_text_within_limits(text):
            return False
    return True
