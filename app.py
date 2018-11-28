from scraper import scraper
from data_accessor import ddb_accessor as ddb
import boto3
import json

# TODO
# done. Add twitter
# done. Stream new twitter submissions to lambda
# redo DynamoDB architecture
# Implement batch Comprehend calls with StartSentimentDetectionJob
# Increase number of reddit submissions analyzed (PRAW subreddit submissions query limit is 1000)
# Index into ElasticSearch
# continuously index streamed data
# Create Lambda function to analyze data (overall sentiment by date)
# Store that information into a SentimentData_<CampaignName> table
# Create UI element to specify items to get by date (submissions show in list) from ElasticSearch
# Show the date's Submissions and overall sentiment when a date is specified
# Prettify UI
# Flag posts requiring attention

# See the *_scratch.json files for the submissions and analysis_results structure templates

lambda_client = boto3.client(service_name='lambda', region_name='us-east-1')


def invoke_reddit_scraper_lambda(query_parameters):
    lambda_client.invoke(
        FunctionName="arn:aws:lambda:us-east-1:433181616955:function:serverless-keywordtracker-dev-hello",
        InvocationType="Event",
        Payload=query_parameters,
    )


def handle_scrape_reddit(event):
    query_parameters = {
        "campaign_name": event["campaign_name"],
        "keywords_list": event["keywords_list"],
        "subreddits_list": event["subreddits_list"],
        "sources": event["sources"]
    }
    print("query_parameters", query_parameters)

    posts = run_reddit_scraper(query_parameters)
    batch_put_posts(posts, "reddit")

    # put PostIds into <campaign_name> table
    post_ids = [post["id"] for post in posts]
    table_name = query_parameters["campaign_name"].replace(" ", "")
    batch_put_ids(post_ids, table_name)

    return posts


def run_reddit_scraper(query_parameters):
    print("running")
    sources = query_parameters["sources"]
    keywords_list = query_parameters["keywords_list"]
    subreddits_list = []
    if "reddit" in sources:
        subreddits_list = query_parameters["subreddits_list"]

    # Scrape the data from sources
    # twitter is polled using a lambda function which triggers my processTweets lambda function when it finds new tweets
    print("scraping")
    reddit_client = scraper.init_reddit_scraper()
    submissions = scraper.scrape_submissions_from_subreddits(reddit_client, subreddits_list, keywords_list)

    print("submissions", submissions)
    return submissions


def handle_campaign_table_operation(event):
    for record in event["Records"]:
        print("record", record)
        if record["eventName"] == "INSERT":
            table_name = record["dynamodb"]["Keys"]["CampaignName"]["S"].replace(" ", "")
            ddb.create_table(table_name)
            query_parameters = extract_campaign_query_params(record["dynamodb"])
            invoke_reddit_scraper_lambda(query_parameters)
        elif record["eventName"] == "REMOVE":
            run_delete_campaign_table(record["dynamodb"])


def extract_campaign_query_params(record):
    table_name = record["Keys"]["CampaignName"]["S"]
    campaign_params_info = record["NewImage"]
    query_parameters = {
        "campaign_name": table_name,
        "keywords_list": campaign_params_info["keywords"]["SS"],
        "subreddits_list": campaign_params_info["subreddits"]["SS"],
        "sources": campaign_params_info["sources"]["SS"]
    }
    return query_parameters


def run_delete_campaign_table(info):
    print("run_delete_table with info", info)
    table_name = info["Keys"]["CampaignName"]["S"].replace(" ", "")
    ddb.delete_table(table_name)


def process_tweets(tweet_data):
    tweets_structure = parse_tweets(tweet_data)
    batch_put_posts(tweets_structure, "twitter")


def parse_tweets(tweet_data):
    tweets_structure = []
    for item in tweet_data:
        jsondata = json.loads(item)  # json.loads() decodes the JSON
        if jsondata["lang"] == 'en':
            tweet = {
                "text": jsondata["text"],
                "date": jsondata["created_at"],  # UTC time
                "user_screen_name": jsondata["user"]["screen_name"],
                "id": jsondata["id_str"],  # will be used in ddb as the PostId
                "truncated": jsondata["truncated"],
            }
            tweets_structure.append(tweet)
    print(tweets_structure)
    return tweets_structure


def batch_put_posts(posts, source):
    ddb.batch_put_posts(posts, source)


def batch_put_ids(post_ids, table_name):
    ddb.batch_put_ids(post_ids, table_name)
