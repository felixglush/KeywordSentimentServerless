import json

from campaign_parameters import CampaignParameters


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


def remove_new_line(post):
    post["title"] = post["title"].replace('\n', ' ')
    post["body"] = post["body"].replace('\n', ' ')
    return post


def remove_new_lines(posts):
    cleaned_posts = [remove_new_line(post) for post in posts]
    return cleaned_posts


def extract_campaign_params_ddb(record):
    campain_name = record["Keys"]["CampaignName"]["S"]
    campaign_params_info = record["NewImage"]

    parameters = CampaignParameters(campain_name, campaign_params_info["sources"]["SS"],
                                    campaign_params_info["keywords"]["SS"], campaign_params_info["subreddits"]["SS"])
    return parameters