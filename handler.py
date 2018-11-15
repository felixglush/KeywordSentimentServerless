import json
import app


def hello(event, context):
    # todo: get query_parameters from event
    print("Printing from event object: ", event["keywords_list"])
    print("Printing from event object: ", event["subreddits_list"])
    print("Printing from event object: ", event["sources"])
    query_parameters = {
        "keywords_list": event["keywords_list"],
        "subreddits_list": event["subreddits_list"],
        "sources": event["sources"]
    }

    result = app.run_scraper(query_parameters)

    body = {
        "message": "Hey there! The function executed successfully!",
        "result": json.dumps(result),
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response


def create_campaign_table(event, context):
    print("DynamoDB trigger called lambda function")
    # app.run_create_table(event["campaign_table_name"])
    body = {
        "message": "Hey there! The function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response