import json
import app


def hello(event, context):
    print("event: ", event)
    print("context: ", context)
    result = app.run()
    print("result", result)
    body = {
        "message": "Hey there! The function executed successfully!",
        "result": result,
        "input": event

    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response
