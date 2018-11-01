import praw

# {"hot":{"subreddit_name":{"title": [], "score": [], "id": [], "url": [], "comms_num": [], "created": [], "body": []},
# "new": {...}}}
# {"hot":{"subreddit_name":{"score": [], "magnitude": [],  ...},
# "new": {...}}}

submissions = {"hot": {}, "new": {}}
analysis_results = {"hot": {}, "new": {}}


def get_id_values():
    file = open("id.txt", "r")
    ids = file.readlines()
    file.close()
    return ids[0].rstrip(), ids[1].rstrip(), ids[2].rstrip(), ids[3].rstrip()


def init_reddit_scraper():
    client_id, client_secret, username, password = get_id_values()
    return praw.Reddit(client_id=client_id,
                       client_secret=client_secret,
                       user_agent="python:keywordtracker:v1.0 (by /u/BrilliantSingletrack)",
                       username=username,
                       password=password)


def setup_structure_for_subreddit(subreddit):
    analysis_results["hot"][subreddit] = {}
    analysis_results["new"][subreddit] = {}

    analysis_results["hot"][subreddit]["title"] = {}
    analysis_results["hot"][subreddit]["body"] = {}
    analysis_results["new"][subreddit]["title"] = {}
    analysis_results["new"][subreddit]["body"] = {}

    analysis_results["hot"][subreddit]["title"]["score"] = []
    analysis_results["hot"][subreddit]["title"]["magnitude"] = []
    analysis_results["hot"][subreddit]["body"]["score"] = []
    analysis_results["hot"][subreddit]["body"]["magnitude"] = []

    analysis_results["new"][subreddit]["title"]["score"] = []
    analysis_results["new"][subreddit]["title"]["magnitude"] = []
    analysis_results["new"][subreddit]["body"]["score"] = []
    analysis_results["new"][subreddit]["body"]["magnitude"] = []

    submissions["hot"][subreddit] = {}
    submissions["new"][subreddit] = {}
    submissions["hot"][subreddit]["title"] = []
    submissions["hot"][subreddit]["score"] = []
    submissions["hot"][subreddit]["id"] = []
    submissions["hot"][subreddit]["url"] = []
    submissions["hot"][subreddit]["comms_num"] = []
    submissions["hot"][subreddit]["created"] = []
    submissions["hot"][subreddit]["body"] = []
    submissions["new"][subreddit]["title"] = []
    submissions["new"][subreddit]["score"] = []
    submissions["new"][subreddit]["id"] = []
    submissions["new"][subreddit]["url"] = []
    submissions["new"][subreddit]["comms_num"] = []
    submissions["new"][subreddit]["created"] = []
    submissions["new"][subreddit]["body"] = []


def get_submissions(reddit, subreddit_name):
    subreddit = reddit.subreddit(subreddit_name)
    subreddit_hot = subreddit.hot()
    subreddit_new = subreddit.new()
    return subreddit_hot, subreddit_new


def iter_submission_type(type, type_string, keywords_list, subreddit):
    for submission in type:
        post_title = submission.title
        post_text = submission.selftext
        for keyword in keywords_list:
            if keyword in post_title or keyword in post_text:
                submissions[type_string][subreddit]["title"].append(post_title)
                submissions[type_string][subreddit]["score"].append(submission.score)  # upvotes
                submissions[type_string][subreddit]["id"].append(submission.id)
                submissions[type_string][subreddit]["url"].append(submission.url)
                submissions[type_string][subreddit]["comms_num"].append(submission.num_comments)
                submissions[type_string][subreddit]["created"].append(submission.created)  # time of creation
                submissions[type_string][subreddit]["body"].append(post_text)  # body text


# Returns two dictionaries: scrapped info for the specified subreddits
# and an analysis_results DS with empty lists for the scores and magnitudes of each submission
def scrape_submissions_from_subreddits(reddit, subreddits_list, keywords_list):
    for subreddit in subreddits_list:
        hot, new = get_submissions(reddit, subreddit)
        setup_structure_for_subreddit(subreddit)
        iter_submission_type(hot, "hot", keywords_list, subreddit)
        iter_submission_type(new, "new", keywords_list, subreddit)
    return submissions, analysis_results


