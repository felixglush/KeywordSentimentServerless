import boto3
import json

comprehend = boto3.client(service_name='comprehend', region_name='us-east-1')


def json_comprehend_sentiment(text):
    return json.dumps(comprehend_sentiment(text))


def comprehend_sentiment(text):
    return comprehend.detect_sentiment(Text=text, LanguageCode='en')


def start_sentiment_detection_job():

    return comprehend.start_sentiment_detection_job(
        InputDataConfig={
            'S3Uri': 's3://keyword-tracker-analysis-input/lines',
            'InputFormat': 'ONE_DOC_PER_LINE'
        },
        OutputDataConfig={
            'S3Uri': 's3://keyword-tracker-analysis-output/lines'
        },
        DataAccessRoleArn='arn:aws:iam::433181616955:role/S3DataAccessRoleForComprehend',
        JobName='KeywordSentimentDetectionJob',
        LanguageCode='en'
    )


# text sent to Amazon Comprehend must be under 5000 bytes
def is_text_within_limits(document):
    return len(document.encode("utf8")) <= 5000 and len(document) > 0


def document_within_limits(text1, text2):
    return is_text_within_limits(text1) and is_text_within_limits(text2)


def add_comprehend_result(analysis_results, subreddit, docs, submission_type_string, text_type_string, keyword):
    target = analysis_results["reddit"][subreddit][submission_type_string][keyword][text_type_string]
    text_list = target["text"]
    sentiment_list = target["Sentiment"]
    sentiment_score_list = target["SentimentScore"]
    response = start_sentiment_detection_job()


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

            add_comprehend_result(analysis_results, subreddit, titles, submission_type_string, "title", key)
            add_comprehend_result(analysis_results, subreddit, bodies, submission_type_string, "body", key)


def analyze_reddit(submissions, analysis_results):
    hot = submissions["hot"]
    new = submissions["new"]
    populate_analysis_results(hot, "hot", analysis_results)
    populate_analysis_results(new, "new", analysis_results)
    return analysis_results
