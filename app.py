import constants
import parser
from campaign_parameters import CampaignParameters
from scraper import reddit_scraper
import data_accessor.dynamodb as ddb
import data_accessor.s3_accessor as s3
import utilities.s3_utils
from sentiment import sentimenter
import boto3
import json
from data_accessor import elasticsearch as es
from utilities.utils import extract_campaign_params_ddb


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

# TODO: write a conditional put operation that does not replace the entire item if it exists.
# Only updates it. But otherwise creates a new item if it exists.
def iterate_through_campaigns_reddit(event):
    response = ddb.scan_table("Campaigns")
    items = response["Items"]
    for item in items:
        print(item)
        # invoke scraper for each campaign
        campaign = CampaignParameters(event["CampaignName"], event["souces"], event["keywords"], event["subreddits"])
        # invoke_reddit_scraper_lambda(campaign)


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
        ddb.batch_put_posts(parser.reddit_posts_list)
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
    try:
        for record in records:
            dynamodb_dump = record["dynamodb"]
            if record["eventName"] == "INSERT" and "Post" in dynamodb_dump["NewImage"]:
                post_ddb_json = dynamodb_dump["NewImage"]["Post"]["M"]
                title = post_ddb_json["title"]["S"]
                body = ""
                if post_ddb_json["body_present"]["BOOL"] == "True":  # TODO handle empty body
                    body = post_ddb_json["body"]["S"]
                bodies.append(body)

                post_id = dynamodb_dump["Keys"]["PostId"]["S"]
                titles.append(title)
                post_ids.append(post_id)
                # TODO index documents into Elasticsearch
            elif record["eventName"] == "MODIFY":
                print("TODO... handle update event")  # TODO update with new sentiment values in Elasticsearch
                new_image = dynamodb_dump["NewImage"]
                post_id = dynamodb_dump["Keys"]["PostId"]["S"]
                if new_image["IsAnalyzed"]["BOOL"] == "True":
                    title_sentiment = new_image["TitleSentiment"]["S"]
                    body_sentiment = new_image["BodySentiment"]["S"]
                    body_sentiment_score = new_image["BodySentimentScore"]
                    title_sentiment_score = new_image["TitleSentimentScore"]
    except KeyError as error:
        print(error)
    return titles, bodies, post_ids


def process_posts_table_stream(event):
    post_titles, post_bodies, post_ids = extract_info_from_streamed_posts_items(event["Records"])
    if len(post_ids) == 0:
        return

    try:
        titles_analysis = sentimenter.analyze_batch_posts(post_titles)
        bodies_analysis = sentimenter.analyze_batch_posts(post_bodies)

        title_results = titles_analysis["ResultList"]
        body_results = bodies_analysis["ResultList"]

        # TODO handle error list
        titles_errors = titles_analysis["ErrorList"]
        body_errors = bodies_analysis["ErrorList"]

        # update each Item in Posts table with analysis results
        ddb.update_posts_with_analysis(title_results, body_results, post_ids)
    except ValueError as error:
        print(error)


def process_s3_sentiment_job(event):
    for record in event["Records"]:
        if record["object"] is not None:
            key = record["object"]["key"]  # full path to tar.gz file containing sentiment data
            print(key)
            s3_object = s3.get_object(constants.s3_output_bucket_name, key)
            sentiment_list = utilities.s3_utils.read_targz_s3_output(s3_object.get()["Body"].read())
            if sentiment_list is not None:
                # put results into Post table
                for item in sentiment_list:
                    print("item", item)


def process_tweets(tweet_data):
    tweets_structure = parser.parse_twitter_tweets(tweet_data)
    ddb.batch_put_posts(tweets_structure)
    return tweets_structure


def elastic():
    print("Elastic function called")
    mock_document = {
        "title": "Moneyball",
        "director": "Bennett Miller",
        "year": "2010"
    }

    es.index(es_index="movies", doc_type="_doc", es_id="6", body=mock_document)
    print(es.get(es_index="movies", doc_type="_doc", es_id="6"))


elastic()