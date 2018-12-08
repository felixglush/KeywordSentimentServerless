import constants
import parser
from campaign_parameters import CampaignParameters
from scraper import reddit_scraper
import data_accessor.ddb_accessor as ddb
import data_accessor.s3_accessor as s3
import data_accessor.s3_utils
from sentiment import sentimenter
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
        # Invokes process_posts_table_stream lambda function and passes 25 posts to it for sentiment analysis until
        # all documents are analyzed
        batch_put_posts(parser.reddit_posts_list)
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


def extract_info_from_streamed_posts_items(records):
    titles, bodies, post_ids = [], [], []
    for record in records:
        if record["eventName"] == "INSERT" and "Post" in record["dynamodb"]["NewImage"]:
            post_ddb_json = record["dynamodb"]["NewImage"]["Post"]["M"]
            title = post_ddb_json["title"]["S"]
            body = ""
            if post_ddb_json["body_present"]["BOOL"] == "True":  # TODO handle empty body
                body = post_ddb_json["body"]["S"]
            bodies.append(body)

            post_id = post_ddb_json["id"]["S"]
            titles.append(title)
            post_ids.append(post_id)
        elif record["eventName"] == "MODIFY":
            print("TODO... handle update event")
    return titles, bodies, post_ids


def process_posts_table_stream(event):
    post_titles, post_bodies, post_ids = extract_info_from_streamed_posts_items(event["Records"])
    if len(post_titles) <= 25 and len(post_bodies) <= 25:
        titles_analysis = sentimenter.analyze_batch_posts(post_titles)
        bodies_analysis = sentimenter.analyze_batch_posts(post_bodies)

        title_results = titles_analysis["ResultList"]
        body_results = bodies_analysis["ResultList"]

        # TODO handle error list
        titles_errors = titles_analysis["ErrorList"]
        body_errors = bodies_analysis["ErrorList"]

        # update each Item in Posts table with analysis results
        ddb.update_posts_with_analysis(title_results, body_results, post_ids)
    else:
        return "Too many posts"


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
    batch_put_posts(tweets_structure)

    # put ids into campaign_name table

    return tweets_structure


def batch_put_posts(posts):
    ddb.batch_put_posts(posts)


def invoke_campaign_iterator():
    lambda_client = boto3.client(service_name='lambda', region_name='us-east-1')
    lambda_client.invoke(
        FunctionName="function:serverless-keywordtracker-dev-iteratePollThroughCampaigns",
        InvocationType="Event"
    )


def check_invoke_campaign_iterator():
    try:
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
    except KeyError:
        print("No such environment variable INVOKE_CAMPAIGN_ITERATOR")


def run_delete_campaign_table(info):
    print("run_delete_table with info", info)
    table_name = info["Keys"]["CampaignName"]["S"].replace(" ", "")
    ddb.delete_table(table_name)
