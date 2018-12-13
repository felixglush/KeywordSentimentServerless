import boto3
import constants
from utilities.sentiment_utils import return_fake_data
from utilities.utils import remove_new_lines
from data_accessor import s3_accessor as s3
import os

comprehend_client = boto3.client(service_name='comprehend', region_name='us-east-1')


# batch_detect_sentiment analyzes at most 25 documents
def analyze_batch_posts(documents):
    num_docs = len(documents)
    if num_docs <= 25:
        try:
            if os.environ["ENABLE_COMPREHEND"] == "true":
                # returns {"ResultList":[], "ErrorList":[]}
                return comprehend_client.batch_detect_sentiment(TextList=documents, LanguageCode='en')
            elif os.environ["ENABLE_COMPREHEND"] == "false":
                # fake sentiment data
                return return_fake_data(num_docs)
        except KeyError:
            print("No such key ENABLE_COMPREHEND")
            return return_fake_data(num_docs)
    else:
        raise ValueError("Too many documents sent for analysis", documents)


def analyze_async_job(posts, query_parameters):
    print("setting up async job")
    cleaned_posts = remove_new_lines(posts)
    metadata = {"campaign_name": query_parameters.name}
    text_container, id_container = s3.setup_docs_for_upload(cleaned_posts, metadata)
    s3.upload_collection(constants.s3_input_bucket_name, text_container, id_container)
    response = start_sentiment_detection_job()
    print("async sentiment analysis job id", response["JobId"])


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

