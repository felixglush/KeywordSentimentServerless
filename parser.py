import json
from scraper import struct_setup as sts
import sentimenter
from scraper.reddit_scraper import keyword_in_text


def parse_twitter_tweets(tweet_data):
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


def parse_reddit_submissions(submission_type, type_string, keywords_list, subreddit):
    for submission in submission_type:
        post_title, post_text = submission.title, submission.selftext
        if sentimenter.documents_within_limits(post_title, post_text):
            for keyword in keywords_list:
                if keyword_in_text(keyword, post_text, post_title):
                    post = {
                        "title": post_title,
                        "body": post_text,
                        "score": str(submission.score),
                        "id": str(submission.id),
                        "url": submission.url,
                        "comms_num": str(submission.num_comments),
                        "date": str(submission.created),
                        "filters": [],  # i.e. hot, new
                        "sentiment": None,
                        "sentiment_score": {}
                    }

                    # append post to list of posts if it is unique
                    subreddit_branch_posts = sts.submissions[type_string][subreddit][keyword]["posts"]
                    post["filters"].append(type_string)
                    if not post_already_exists(submission.id, subreddit_branch_posts):
                        subreddit_branch_posts.append(post)

                    # subreddit_branch["title"].append(post_title)
                    # subreddit_branch["score"].append(str(submission.score))  # upvotes
                    # subreddit_branch["id"].append(str(submission.id))
                    # subreddit_branch["url"].append(submission.url)
                    # subreddit_branch["comms_num"].append(str(submission.num_comments))
                    # subreddit_branch["created"].append(str(submission.created))  # time of creation
                    # subreddit_branch["body"].append(post_text)  # body text


def post_already_exists(post_id, posts):
    for post in posts:
        if post["id"] == str(post_id):
            return True
    return False


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
