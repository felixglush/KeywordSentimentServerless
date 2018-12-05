import praw
import parser
from scraper import struct_setup as sts


def get_id_values():
    file = open("id.txt", "r")
    ids = file.readlines()
    file.close()
    return ids[0].strip(), ids[1].strip(), ids[2].strip(), ids[3].strip()


def init_reddit_scraper():
    client_id, client_secret, username, password = get_id_values()
    return praw.Reddit(client_id=client_id,
                       client_secret=client_secret,
                       user_agent="python:keywordtracker:v1.0 (by /u/BrilliantSingletrack)",
                       username=username,
                       password=password)


def get_submissions(reddit_client, subreddit_name):
    subreddit = reddit_client.subreddit(subreddit_name)
    subreddit_hot = subreddit.hot()
    subreddit_new = subreddit.new()
    return subreddit_hot, subreddit_new


def keyword_in_text(keyword, post_text, post_title):
    return (' ' + keyword + ' ') in (' ' + post_title + ' ') or \
           (' ' + keyword + ' ') in (' ' + post_text + ' ')


# Returns two dictionaries: scrapped info for the specified subreddits
# and an analysis_results DS with empty lists for the scores and magnitudes of each submission
def scrape_submissions_from_subreddits(reddit_client, subreddits_list, keywords_list):
    sts.submissions = {"hot": {}, "new": {}}
    sts.analysis_results = {"reddit": {}}
    sts.analysis_results["reddit"]["subreddits"] = []
    for subreddit in subreddits_list:
        hot, new = get_submissions(reddit_client, subreddit)
        data = {"subreddit": subreddit, "keywords_list": keywords_list}
        sts.setup_structure("reddit", data)
        parser.parse_reddit_submissions(hot, "hot", keywords_list, subreddit)
        parser.parse_reddit_submissions(new, "new", keywords_list, subreddit)
    return sts.submissions, sts.analysis_results
