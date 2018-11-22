import boto3
import json

comprehend = boto3.client(service_name='comprehend', region_name='us-east-1')


def json_comprehend_sentiment(text):
    return json.dumps(comprehend_sentiment(text))


def comprehend_sentiment(text):
    return comprehend.detect_sentiment(Text=text, LanguageCode='en')


# No more than 25 items can be in text_list
def batch_comprehend_sentiment(text_list):
    return comprehend.batch_detect_sentiment(TextList=text_list)


# text sent to Amazon Comprehend must be under 5000 bytes
def is_text_over_limits(document):
    return len(document.encode("utf8")) > 5000


def filter_document_over_limits(docs):
    return [document for document in docs if not is_text_over_limits(document)]


def add_comprehend_result(analysis_results, subreddit, text, submission_type_string, text_type_string, keyword):
    target = analysis_results["reddit"][subreddit][submission_type_string][keyword][text_type_string]
    text_list = target["text"]
    sentiment_list = target["Sentiment"]
    sentiment_score_list = target["SentimentScore"]
    if len(text) > 0 and not is_text_over_limits(text):
        comprehend_result = comprehend_sentiment(text)
        sentiment = comprehend_result['Sentiment']
        sentiment_score = {
            "Mixed": str(comprehend_result["SentimentScore"]["Mixed"]),
            "Positive": str(comprehend_result["SentimentScore"]["Positive"]),
            "Negative": str(comprehend_result["SentimentScore"]["Negative"]),
            "Neutral": str(comprehend_result["SentimentScore"]["Neutral"])
        }
        text_list.append(text)
        sentiment_list.append(sentiment)
        sentiment_score_list.append(sentiment_score)
    else:
        text_list.append(" ")
        sentiment_list.append(" ")
        sentiment_score_list.append(None)


def add_auxiliary_data(analysis_results, key, submission_type, submission_type_string, subreddit):
    key_target = analysis_results["reddit"][subreddit][submission_type_string][key]
    key_target["urls"] = submission_type[subreddit][key]["url"]
    key_target["ids"] = submission_type[subreddit][key]["id"]
    key_target["upvotes"] = submission_type[subreddit][key]["score"]
    key_target["creation_dates"] = submission_type[subreddit][key]["created"]


def populate_analysis_results(submission_type, submission_type_string, analysis_results):
    for subreddit in submission_type:
        for key in submission_type[subreddit]:
            titles = submission_type[subreddit][key]["title"]
            bodies = submission_type[subreddit][key]["body"]
            add_auxiliary_data(analysis_results, key, submission_type, submission_type_string, subreddit)
            for title_text in titles:
                add_comprehend_result(analysis_results, subreddit, title_text,
                                      submission_type_string, "title", key)

            for body_text in bodies:
                add_comprehend_result(analysis_results, subreddit, body_text,
                                      submission_type_string, "body", key)


def analyze(submissions, analysis_results):
    hot = submissions["hot"]
    new = submissions["new"]
    populate_analysis_results(hot, "hot", analysis_results)
    populate_analysis_results(new, "new", analysis_results)
    return analysis_results
