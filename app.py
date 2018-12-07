import constants
import parser
from campaign_parameters import CampaignParameters
from scraper import reddit_scraper
import data_accessor.ddb_accessor as ddb
import data_accessor.s3_accessor as s3
import data_accessor.s3_utils
import sentimenter
import time
import boto3
import json
import os
from utils import extract_campaign_params_ddb
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


def invoke_reddit_scraper_lambda(campaign_parameters):
    lambda_client = boto3.client(service_name='lambda', region_name='us-east-1')
    lambda_client.invoke(
        FunctionName="arn:aws:lambda:us-east-1:433181616955:function:serverless-keywordtracker-dev-scrapeReddit",
        InvocationType="Event",
        Payload=json.dumps(campaign_parameters.__dict__),
    )


def handle_scrape_reddit(event):
    query_parameters = CampaignParameters(event["name"], event["sources"],
                                          event["keywords"], event["subreddits"])

    print("query_parameters", query_parameters)
    if "reddit" in query_parameters.sources:
        submissions = run_reddit_scraper(query_parameters)
        # DDB Stream enabled on Posts table.
        # Invokes process_posts_table_stream lambda function and passes 25 posts to it for sentiment analysis.
        batch_put_posts(parser.reddit_posts_list, "reddit")
        return submissions
    return None


def run_reddit_scraper(query_parameters):
    print("running scraper")
    reddit_client = reddit_scraper.init_reddit_scraper()
    submissions = reddit_scraper.scrape_submissions_from_subreddits(reddit_client,
                                                                    query_parameters.subreddits,
                                                                    query_parameters.keywords)
    print("reddit submissions", submissions)
    return submissions


def process_campaign_table_stream(event):
    for record in event["Records"]:
        print("record", record)
        if record["eventName"] == "INSERT":
            query_parameters = extract_campaign_params_ddb(record["dynamodb"])
            if "reddit" in query_parameters.sources:
                invoke_reddit_scraper_lambda(query_parameters)
            if "twitter" in query_parameters.sources:
                # TODO: twitter
                print("todo... invoke twitter search")


def process_posts_table_stream(event):
    return None


def process_s3_sentiment_job(event):
    for record in event["Records"]:
        if record["object"] is not None:
            key = record["object"]["key"]  # full path to tar.gz file containing sentiment data
            print(key)
            s3_object = s3.get_object(constants.s3_output_bucket_name, key)
            sentiment_list = data_accessor.s3_utils.read_targz_s3_output(s3_object.get()["Body"].read())
            if sentiment_list is not None:
                for item in sentiment_list:
                    print("item", item)
                # put results into Post table


def process_tweets(tweet_data):
    tweets_structure = parser.parse_twitter_tweets(tweet_data)
    # sentimenter.analyze_tweets(tweets_structure)  # will modify tweets_structure by inputting sentiment data
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