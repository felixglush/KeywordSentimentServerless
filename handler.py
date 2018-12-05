import app
from utils import create_ok_response, log_lambda_trigger


def scrape_reddit(event, context):
    log_lambda_trigger(event, "scrape_reddit")
    submissions = app.handle_scrape_reddit(event)
    return create_ok_response(event=event, result=submissions, func_name="scrape_reddit")


# Triggered by putting/deleting an item in Campaigns table by enabling a DynamoDB stream on the table
# Item is passed to this function in the event parameter
def handle_campaign_table_operation(event, context):
    log_lambda_trigger(event, "handle_campaign_table_operation", "A DynamoDB event trigger")
    app.handle_campaign_table_operation(event)
    return create_ok_response(event=event, func_name="handle_campaign_table_operation")


# Triggered by an application that polls the Twitter API using a Cloudwatch rule with a given search text.
def process_tweets(event, context):
    log_lambda_trigger(event, "process_tweets")
    tweets = app.process_tweets(event)
    return create_ok_response(event=event, result=tweets, func_name="process_tweets")


def iterate_poll_through_campaigns(event, context):
    log_lambda_trigger(event, "iterate_poll_through_campaigns")
    app.iterate_and_poll_through_campaigns()
    return create_ok_response(event=event, func_name="iterate_poll_through_campaigns")
