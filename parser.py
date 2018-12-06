import json
from scraper import struct_setup as sts
import sentimenter
from scraper import reddit_scraper


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


reddit_posts_list = []


def append_filter_to_post(type_string, post_id):
    for i in range(len(reddit_posts_list)):
        if reddit_posts_list[i]["id"] == post_id:
            reddit_posts_list[i]["filters"].append(type_string)


def parse_reddit_submissions(submission_type, type_string, keywords_list, subreddit):
    for submission in submission_type:
        post_title, post_text = submission.title, submission.selftext
        if sentimenter.documents_within_limits(post_title, post_text):
            for keyword in keywords_list:
                if reddit_scraper.keyword_in_text(keyword, post_text, post_title):
                    if not post_already_exists(str(submission.id), reddit_posts_list):
                        post = {
                            "title": post_title,
                            "body": post_text,
                            "score": str(submission.score),
                            "id": str(submission.id),
                            "url": submission.url,
                            "comms_num": str(submission.num_comments),
                            "date": str(submission.created),
                            "filters": [type_string],  # i.e. hot, new
                            "sentiment": None,
                            "sentiment_score": {}
                        }
                        subreddit_branch_posts = sts.submissions[type_string][subreddit][keyword]["posts"]
                        subreddit_branch_posts.append(post)
                        reddit_posts_list.append(post)
                    else:
                        append_filter_to_post(type_string, str(submission.id))


def post_already_exists(post_id, posts):
    list_of_ids = [post["id"] for post in posts]
    return post_id in list_of_ids


