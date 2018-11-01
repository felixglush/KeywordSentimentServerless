import boto3

comprehend = boto3.client(service_name='comprehend', region_name='us-east-1')


def comprehend_sentiment(text):
    return comprehend.detect_sentiment(Text=text, LanguageCode='en')


def add_comprehend_result(analysis_results, subreddit, text, submission_type_string, text_type_string):
    text_list = analysis_results[submission_type_string][subreddit][text_type_string]["text"]
    sentiment_list = analysis_results[submission_type_string][subreddit][text_type_string]["Sentiment"]
    sentiment_score_list = analysis_results[submission_type_string][subreddit][text_type_string]["SentimentScore"]
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


def populate_analysis_results(submission_type, submission_type_string, analysis_results):
    for subreddit in submission_type:
        titles = submission_type[subreddit]["title"]
        bodies = submission_type[subreddit]["body"]

        for title_text in titles:
            add_comprehend_result(analysis_results, subreddit, title_text, submission_type_string, "title")

        for body_text in bodies:
            add_comprehend_result(analysis_results, subreddit, body_text, submission_type_string, "body")


def analyze(submissions, analysis_results):
    hot = submissions["hot"]
    new = submissions["new"]
    populate_analysis_results(hot, "hot", analysis_results)
    populate_analysis_results(new, "new", analysis_results)
    return analysis_results
