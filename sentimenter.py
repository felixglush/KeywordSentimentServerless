import boto3
import constants
from data_accessor import s3_accessor as s3
comprehend_client = boto3.client(service_name='comprehend', region_name='us-east-1')


def analyze_async_job(posts):
    text_file, ids_file = s3.setup_files(posts)
    s3.upload_files(constants.s3_input_bucket, text_file, ids_file)
    start_sentiment_detection_job()


def start_sentiment_detection_job():
    return comprehend_client.start_sentiment_detection_job(
        InputDataConfig={
            'S3Uri': constants.s3_input_bucket + constants.s3_bucket_texts,
            'InputFormat': 'ONE_DOC_PER_LINE'
        },
        OutputDataConfig={
            'S3Uri': constants.s3_output_bucket + constants.s3_bucket_texts
        },
        DataAccessRoleArn=constants.s3_data_access_role_arn,
        JobName=constants.s3_comprehend_sentiment_detection_job_name,
        LanguageCode='en'
    )


def analyze_tweets(tweets_structure):
    text_list = [tweet["text"] for tweet in tweets_structure]
    results = analyze_batch_posts(text_list)
    for result in results["ResultList"]:
        index = result["Index"]
        sentiment = result["Sentiment"]
        sentiment_score = result["SentimentScore"]
        tweets_structure[index]["sentiment"] = sentiment
        tweets_structure[index]["sentiment_score"] = sentiment_score


def analyze_batch_posts(documents):
    return comprehend_client.batch_detect_sentiment(TextList=documents, LanguageCode='en')


# text sent to Amazon Comprehend must be under 5000 bytes
def is_text_within_limits(document):
    return len(document.encode("utf8")) <= 5000 and len(document) > 0


def documents_within_limits(*text_list):
    for text in text_list:
        if not is_text_within_limits(text):
            return False
    return True

# def add_auxiliary_data(analysis_results, key, submission_type, submission_type_string, subreddit):
#     key_target = analysis_results["reddit"][subreddit][submission_type_string][key]
#     key_target["urls"] = submission_type[subreddit][key]["url"]
#     key_target["ids"] = submission_type[subreddit][key]["id"]
#     key_target["upvotes"] = submission_type[subreddit][key]["score"]
#     key_target["creation_dates"] = submission_type[subreddit][key]["created"]
#
#
# def populate_analysis_results(submission_type, submission_type_string, analysis_results):
#     for subreddit in submission_type:
#         for key in submission_type[subreddit]:
#             titles = submission_type[subreddit][key]["title"]
#             bodies = submission_type[subreddit][key]["body"]
#             add_auxiliary_data(analysis_results, key, submission_type, submission_type_string, subreddit)
#
#             add_comprehend_result(analysis_results, subreddit, titles, submission_type_string, "title", key)
#             add_comprehend_result(analysis_results, subreddit, bodies, submission_type_string, "body", key)
#
#
# def analyze_reddit(submissions, analysis_results):
#     hot = submissions["hot"]
#     new = submissions["new"]
#     populate_analysis_results(hot, "hot", analysis_results)
#     populate_analysis_results(new, "new", analysis_results)
#     return analysis_results
