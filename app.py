import scraper
import sentimenter


# {"hot":{"subreddit_name":{"title": [], "score": [], "id": [], "url": [], "comms_num": [], "created": [], "body": []},
# "new": {...}}}

def run():
    keywords_list = ["The"]
    subreddits_list = ["uwaterloo"]

    reddit = scraper.init_reddit_scraper()
    submissions, analysis_results = scraper.scrape_submissions_from_subreddits(reddit, subreddits_list, keywords_list)
    sentimenter.analyze(submissions, analysis_results)  # (desired) side effect: analysis_results will be modified.

    return analysis_results
