import boto3
import json

comprehend = boto3.client(service_name='comprehend', region_name='us-east-1')


def json_comprehend_sentiment(text):
    return json.dumps(comprehend_sentiment(text))


def comprehend_sentiment(text):
    return comprehend.detect_sentiment(Text=text, LanguageCode='en')


def add_comprehend_result(analysis_results, subreddit, text, submission_type_string, text_type_string, keyword):
    target = analysis_results["reddit"][subreddit][submission_type_string][keyword][text_type_string]
    text_list = target["text"]
    sentiment_list = target["Sentiment"]
    sentiment_score_list = target["SentimentScore"]
    if len(text) > 0:
        comprehend_result = comprehend_sentiment(text)
        sentiment = comprehend_result['Sentiment']
        sentiment_score_object = comprehend_result["SentimentScore"]
        text_list.append(text)
        sentiment_list.append(sentiment)
        sentiment_score_list.append(sentiment_score_object)
    else:
        text_list.append("")
        sentiment_list.append("")
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
