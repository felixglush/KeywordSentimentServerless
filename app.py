import parser
from scraper import reddit_scraper
from data_accessor import ddb_accessor as ddb
import sentimenter
import boto3

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


def invoke_reddit_scraper_lambda(query_parameters):
    lambda_client = boto3.client(service_name='lambda', region_name='us-east-1')
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
    sentimenter.analyze_async_job(posts)  # modifies posts
    batch_put_posts(posts, "reddit")

    # put PostIds into <campaign_name> table
    post_ids = [post["id"] for post in posts]
    table_name = query_parameters["campaign_name"].replace(" ", "")
    batch_put_ids(post_ids, table_name)

    return posts


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
            table_name = record["dynamodb"]["Keys"]["CampaignName"]["S"].replace(" ", "")
            ddb.create_table(table_name)
            query_parameters = parser.extract_campaign_query_params(record["dynamodb"])
            invoke_reddit_scraper_lambda(query_parameters)
        elif record["eventName"] == "REMOVE":
            run_delete_campaign_table(record["dynamodb"])


def run_delete_campaign_table(info):
    print("run_delete_table with info", info)
    table_name = info["Keys"]["CampaignName"]["S"].replace(" ", "")
    ddb.delete_table(table_name)


def process_tweets(tweet_data):
    tweets_structure = parser.parse_twitter_tweets(tweet_data)
    sentimenter.analyze_tweets(tweets_structure)  # will modify tweets_structure by inputting sentiment data
    batch_put_posts(tweets_structure, "twitter")
    return tweets_structure


def batch_put_posts(posts, source):
    ddb.batch_put_posts(posts, source)


def batch_put_ids(post_ids, table_name):
    ddb.batch_put_ids(post_ids, table_name)
