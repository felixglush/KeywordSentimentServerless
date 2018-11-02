import json
import app


def hello(event, context):
    # todo: get query_parameters from event
    query_parameters = {
        "keywords_list": ["The"],
        "subreddits_list": ["uwaterloo"],
        "sources": ["reddit"]
    }

    result = app.run(query_parameters)

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
