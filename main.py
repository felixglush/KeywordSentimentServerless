import model
import scraper

# {"hot":{"subreddit_name":{"title": [], "score": [], "id": [], "url": [], "comms_num": [], "created": [], "body": []},
# "new": {...}}}



def run():
    keywords_list = ["The"]
    subreddits_list = ["uwaterloo"]
    the_model = model.Model()
    the_model.set_params(keywords_list, subreddits_list)
    reddit = scraper.init_reddit_scraper()
    print(reddit.user.me())
    # submissions, analysis_results = scraper.scrape_submissions_from_subreddits(reddit, model.get_params().subreddits,
    #                                                                            model.get_params().keywords)
    # model.set_submissions(submissions)


def analyze_type(submission_type, type_string):
    pass


def analyze():
    pass
    # hot = submissions["hot"]
    # new = submissions["new"]
    # analyze_type(hot, "hot")
    # analyze_type(new, "new")