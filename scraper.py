import praw
import struct_setup as sts


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


def get_submissions(reddit, subreddit_name):
    subreddit = reddit.subreddit(subreddit_name)
    subreddit_hot = subreddit.hot()
    subreddit_new = subreddit.new()
    return subreddit_hot, subreddit_new


def iter_submission_type(submission_type, type_string, keywords_list, subreddit):
    for submission in submission_type:
        post_title = submission.title
        post_text = submission.selftext
        for keyword in keywords_list:
            if keyword in post_title or keyword in post_text:
                subreddit_branch = sts.submissions[type_string][subreddit][keyword]
                subreddit_branch["title"].append(post_title)
                subreddit_branch["score"].append(submission.score)  # upvotes
                subreddit_branch["id"].append(submission.id)
                subreddit_branch["url"].append(submission.url)
                subreddit_branch["comms_num"].append(submission.num_comments)
                subreddit_branch["created"].append(submission.created)  # time of creation
                subreddit_branch["body"].append(post_text)  # body text


# Returns two dictionaries: scrapped info for the specified subreddits
# and an analysis_results DS with empty lists for the scores and magnitudes of each submission
def scrape_submissions_from_subreddits(reddit, subreddits_list, keywords_list):
    for subreddit in subreddits_list:
        hot, new = get_submissions(reddit, subreddit)
        data = {"subreddit": subreddit, "keywords_list": keywords_list}
        sts.setup_structure("reddit", data)
        iter_submission_type(hot, "hot", keywords_list, subreddit)
        iter_submission_type(new, "new", keywords_list, subreddit)
    return sts.submissions, sts.analysis_results


