import boto3
import constants
from data_accessor import s3_accessor as s3
from utils import remove_new_lines

comprehend_client = boto3.client(service_name='comprehend', region_name='us-east-1')


def analyze_async_job(posts, query_parameters):
    print("setting up async job")
    cleaned_posts = remove_new_lines(posts)
    metadata = {"campaign_name": query_parameters["campaign_name"]}
    # text_container, id_container = s3.setup_docs_for_upload(cleaned_posts, metadata)
    # s3.upload_collection(constants.s3_input_bucket_name, text_container, id_container)
    # response = start_sentiment_detection_job()
    # print("job id", response["JobId"])
    # TODO remove s3.get_object(..) below. let s3 event trigger lambda
    s3.get_object(constants.s3_output_bucket_name, None)


def start_sentiment_detection_job():
    return comprehend_client.start_sentiment_detection_job(
        InputDataConfig={
            'S3Uri': constants.s3_input_bucket_uri,
            'InputFormat': 'ONE_DOC_PER_LINE'
        },
        OutputDataConfig={
            'S3Uri': constants.s3_output_bucket_uri
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
