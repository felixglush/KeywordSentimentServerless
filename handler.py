import app
from utils import create_ok_response, log_lambda_trigger


def scrape_reddit(event, context):
    log_lambda_trigger(event, "scrape_reddit")
    submissions = app.handle_scrape_reddit(event)
    return create_ok_response(event, submissions, "scrape_reddit")


# Triggered by putting/deleting an item in Campaigns table by enabling a DynamoDB stream on the table
# Item is passed to this function in the event parameter
def handle_campaign_table_operation(event, context):
    log_lambda_trigger(event, "handle_campaign_table_operation", "A DynamoDB event trigger")
    app.handle_campaign_table_operation(event)
    return create_ok_response(event, "handle_campaign_table_operation")


# Triggered by a serverless application that polls the Twitter API using a Cloudwatch rule.
def process_tweets(event, context):
    log_lambda_trigger(event, "process_tweets")
    tweets = app.process_tweets(event)
    return create_ok_response(event, tweets, "process_tweets")
