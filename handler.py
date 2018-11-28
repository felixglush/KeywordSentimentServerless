import json
import app


def scrape_reddit(event, context):
    log_trigger(event, "scrape_reddit")
    result = app.handle_scrape_reddit(event)
    return create_ok_response(event, result, "scrape_reddit")


# Triggered by putting/deleting an item in Campaigns table by enabling a DynamoDB stream on the table
# Item is passed to this function in the event parameter
def handle_campaign_table_operation(event, context):
    log_trigger(event, "handle_campaign_table_operation", "A DynamoDB event trigger")
    app.handle_campaign_table_operation(event)
    return create_ok_response(event, "handle_campaign_table_operation")


def process_tweets(event, context):
    log_trigger(event, "process_tweets")
    app.process_tweets(event)
    return create_ok_response(event, "process_tweets")


def create_ok_response(event, result=None, func_name="lambda"):
    body = {
        "message": "Hey there! The " + func_name + " function executed successfully!",
        "result": json.dumps(result),
        "input": event
    }
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response


def log_trigger(event, func_name, who=""):
    print("{} invoked lambda {} function with event {}".format(who, func_name, event))
