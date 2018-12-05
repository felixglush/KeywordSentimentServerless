import constants
import parser
from scraper import reddit_scraper
from data_accessor import ddb_accessor as ddb
import sentimenter
import time
import boto3
import json
import os
# TODO
# done. Add twitter
# done. Stream new twitter submissions to lambda
# done. redo DynamoDB architecture
# done. Implement batch Comprehend calls with StartSentimentDetectionJob
# Increase number of reddit submissions analyzed (PRAW subreddit submissions query limit is 1000)
# Index into ElasticSearch
# continuously index streamed data
# Create Lambda function to analyze data (overall sentiment by date)
# Store that information into a SentimentData_<CampaignName> table
# Create UI element to specify items to get by date (submissions show in list) from ElasticSearch
# Show the date's Submissions and overall sentiment when a date is specified
# Prettify UI
# Flag posts requiring attention


def invoke_reddit_scraper_lambda(query_parameters):
    lambda_client = boto3.client(service_name='lambda', region_name='us-east-1')
    lambda_client.invoke(
        FunctionName="arn:aws:lambda:us-east-1:433181616955:function:serverless-keywordtracker-dev-hello",
        InvocationType="Event",
        Payload=json.dumps(query_parameters),
    )


def handle_scrape_reddit(event):
    query_parameters = {
        "campaign_name": event["campaign_name"],
        "keywords_list": event["keywords_list"],
        "subreddits_list": event["subreddits_list"],
        "sources": event["sources"]
    }
    print("query_parameters", query_parameters)
    parser.reddit_posts_list = []
    responses = run_reddit_scraper(query_parameters)
    sentimenter.analyze_async_job(parser.reddit_posts_list)  # modifies responses
    batch_put_posts(parser.reddit_posts_list, "reddit")

    # put PostIds into <campaign_name> table
    # table_name = query_parameters["campaign_name"].replace(" ", "")
    # post_ids = [post["id"] for post in parser.reddit_posts_list]
    # batch_put_ids(post_ids, table_name)

    return responses


def run_reddit_scraper(query_parameters):
    print("running scraper")
    subreddits_list = []
    if "reddit" in query_parameters["sources"]:
        subreddits_list = query_parameters["subreddits_list"]

    reddit_client = reddit_scraper.init_reddit_scraper()
    submissions = reddit_scraper.scrape_submissions_from_subreddits(reddit_client, subreddits_list,
                                                                    query_parameters["keywords_list"])

    print("reddit submissions", submissions)
    return submissions


def handle_campaign_table_operation(event):
    for record in event["Records"]:
        print("record", record)
        if record["eventName"] == "INSERT":
            #table_name = record["dynamodb"]["Keys"]["CampaignName"]["S"].replace(" ", "")
            #ddb.create_table(table_name)
            query_parameters = parser.extract_campaign_query_params(record["dynamodb"])
            invoke_reddit_scraper_lambda(query_parameters)
            # check_invoke_campaign_iterator()
        elif record["eventName"] == "REMOVE":
            run_delete_campaign_table(record["dynamodb"])


def check_invoke_campaign_iterator():
    if os.environ["INVOKE_CAMPAIGN_ITERATOR"] == "true":
        print("invoking function iteratePollThroughCampaigns")
        invoke_campaign_iterator()
        lambda_client = boto3.client(service_name='lambda', region_name='us-east-1')
        lambda_client.update_function_configuration(
            FunctionName='function:serverless-keywordtracker-dev-iteratePollThroughCampaigns',
            Environment={
                'Variables': {
                    'INVOKE_CAMPAIGN_ITERATOR': "false",
                }
            }
        )


def run_delete_campaign_table(info):
    print("run_delete_table with info", info)
    table_name = info["Keys"]["CampaignName"]["S"].replace(" ", "")
    ddb.delete_table(table_name)


def process_tweets(tweet_data):
    tweets_structure = parser.parse_twitter_tweets(tweet_data)
    #sentimenter.analyze_tweets(tweets_structure)  # will modify tweets_structure by inputting sentiment data
    batch_put_posts(tweets_structure, "twitter")

    # put ids into campaign_name table

    return tweets_structure


def batch_put_posts(posts, source):
    ddb.batch_put_posts(posts, source)


def batch_put_ids(post_ids, table_name):
    ddb.batch_put_ids(post_ids, table_name)


def iterate_and_poll_through_campaigns():
    lambda_client = boto3.client(service_name='lambda', region_name='us-east-1')
    ddb_resource = boto3.resource('dynamodb', region_name='us-east-1')
    campaign_table = ddb_resource.Table("Campaigns")
    response = campaign_table.scan()
    items = response["Items"]
    count = response["Count"]
    timeout = count * constants.sleep_time_for_campaign_poll + 20
    lambda_client.update_function_configuration(
        FunctionName='function:serverless-keywordtracker-dev-iteratePollThroughCampaigns',
        Timeout=timeout
    )

    cloudwatch_client = boto3.client('events')
    if len(items) != 0:
        cloudwatch_client.enable_rule(
            Name='aws-serverless-repository-TwitterSearchPollerTimer-16ZY6SG281Q6X'
        )
    time.sleep(10)
    print('items', items)

    for campaign in items:
        query_parameters = {
            "campaign_name": campaign["CampaignName"],
            "sources": campaign["sources"],
            "keywords": campaign["keywords"],
            "subreddits": campaign["subreddits"]
        }
        print("Campaign parameters", query_parameters)

        # update twitter poller lambda function configuration
        search_text = ' OR '.join(query_parameters["keywords"])
        response = lambda_client.update_function_configuration(
            FunctionName='aws-serverless-repository-aws-TwitterSearchPoller-6GH8Y61OUDGH',
            Environment={
                'Variables': {
                    'SEARCH_TEXT': search_text,
                }
            }
        )

        # now the poller will automatically invoke the processTweets lambda function with the keywords of the campaign
        time.sleep(constants.sleep_time_for_campaign_poll)

    # stop the poller once done
    cloudwatch_client.disable_rule(
        Name='aws-serverless-repository-TwitterSearchPollerTimer-16ZY6SG281Q6X'
    )

    print("REINVOKE_CAMPAIGN_ITERATOR", os.environ["REINVOKE_CAMPAIGN_ITERATOR"])
    if os.environ["REINVOKE_CAMPAIGN_ITERATOR"] == "true":
        print("reinvoking iteratePollThroughCampaigns")
        invoke_campaign_iterator()


def invoke_campaign_iterator():
    lambda_client = boto3.client(service_name='lambda', region_name='us-east-1')
    lambda_client.invoke(
        FunctionName="function:serverless-keywordtracker-dev-iteratePollThroughCampaigns",
        InvocationType="Event"
    )
