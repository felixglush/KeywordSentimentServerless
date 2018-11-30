import json


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


def log_lambda_trigger(event, func_name, who=""):
    print("{} invoked lambda {} function with event {}".format(who, func_name, event))


def is_empty_string(string):
    return string == "" or string is None
