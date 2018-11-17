import json
import app


def scrape(event, context):
    query_parameters = {
        "keywords_list": event["keywords_list"],
        "subreddits_list": event["subreddits_list"],
        "sources": event["sources"]
    }
    print("query_parameters", query_parameters)

    result = app.run_scraper(query_parameters)

    body = {
        "message": "Hey there! The scrape function executed successfully!",
        "result": json.dumps(result),
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response


# Triggered by putting an item into Campaigns table by enabling a DynamoDB stream on the table
# Item is passed to this function in the event parameter
def handle_campaign_table_operation(event, context):
    print("DynamoDB triggered lambda function")
    print("event", event)

    for record in event["Records"]:
        print("record", record)
        if record["eventName"] == "INSERT":
            app.run_create_table(record["dynamodb"])
        elif record["eventName"] == "REMOVE":
            app.run_delete_table(record["dynamodb"])

    body = {
        "message": "Hey there! The create_campaign_table function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

