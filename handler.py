import app
from utilities.utils import create_ok_response, log_lambda_trigger


def scrape_reddit(event, context):
    log_lambda_trigger(event, "scrape_reddit")
    submissions = app.handle_scrape_reddit(event)
    return create_ok_response(event=event, result=submissions, func_name="scrape_reddit")


# Triggered by putting/deleting an item in Campaigns table by enabling a DynamoDB stream on the table
# Item is passed to this function in the event parameter
def process_campaign_table_stream(event, context):
    log_lambda_trigger(event, "process_campaign_table_stream", "A DynamoDB event trigger")
    app.process_campaign_table_stream(event)
    return create_ok_response(event=event, func_name="process_campaign_table_stream")


# Triggered by an application that polls the Twitter API using a Cloudwatch rule with a given search text.
def process_tweets(event, context):
    log_lambda_trigger(event, "process_tweets")
    tweets = app.process_tweets(event)
    return create_ok_response(event=event, result=tweets, func_name="process_tweets")


def iterate_through_campaigns_reddit(event, context):
    log_lambda_trigger(event, "iterate_through_campaigns_reddit")
    app.iterate_through_campaigns_reddit(event)
    return create_ok_response(event=event, func_name="iterate_through_campaigns_reddit")


def process_s3_sentiment_job(event, context):
    log_lambda_trigger(event, "process_s3_sentiment_job")
    app.process_s3_sentiment_job(event)
    return create_ok_response(event=event, func_name="process_s3_sentiment_job")


def process_posts_table_stream(event, context):
    log_lambda_trigger(event, "process_posts_table_stream")
    result = app.process_posts_table_stream(event)
    return create_ok_response(event=event, result=result, func_name="process_posts_table_stream")

