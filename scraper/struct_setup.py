submissions = {"hot": {}, "new": {}}
analysis_results = {}


def setup_structure_for_subreddit(subreddit, keywords_list):
    submissions["hot"][subreddit] = {}
    submissions["new"][subreddit] = {}
    analysis_results["reddit"]["subreddits"].append(subreddit)
    analysis_results["reddit"][subreddit] = {}
    analysis_results["reddit"][subreddit]["hot"] = {}
    analysis_results["reddit"][subreddit]["new"] = {}
    hot_branch = analysis_results["reddit"][subreddit]["hot"]
    new_branch = analysis_results["reddit"][subreddit]["new"]
    for key in keywords_list:
        print("setting up keyword", key)
        hot_branch[key] = {}
        hot_branch[key]["urls"] = []
        hot_branch[key]["ids"] = []
        hot_branch[key]["upvotes"] = []
        hot_branch[key]["creation_dates"] = []
        hot_branch[key]["title"] = {}
        hot_branch[key]["body"] = {}
        hot_branch[key]["title"]["text"] = []
        hot_branch[key]["title"]["Sentiment"] = []
        hot_branch[key]["title"]["SentimentScore"] = []
        hot_branch[key]["body"]["text"] = []
        hot_branch[key]["body"]["Sentiment"] = []
        hot_branch[key]["body"]["SentimentScore"] = []

        new_branch[key] = {}
        new_branch[key]["urls"] = []
        new_branch[key]["ids"] = []
        new_branch[key]["upvotes"] = []
        new_branch[key]["creation_dates"] = []
        new_branch[key]["title"] = {}
        new_branch[key]["body"] = {}
        new_branch[key]["title"]["text"] = []
        new_branch[key]["title"]["Sentiment"] = []
        new_branch[key]["title"]["SentimentScore"] = []
        new_branch[key]["body"]["text"] = []
        new_branch[key]["body"]["Sentiment"] = []
        new_branch[key]["body"]["SentimentScore"] = []

        # {"hot":{"subreddit_name":{"title": [], "score": [], "id": [], "url": [], "comms_num": [], "created": [], "body": []},
        # "new": {...}}}
        # {"hot":{"subreddit_name":{"Sentiment": [], "SentimentScore": [],  ...},
        # "new": {...}}}

        submissions["hot"][subreddit][key] = {}
        # hot_keyword_object = submissions["hot"][subreddit][key]
        submissions["hot"][subreddit][key]["title"] = []
        submissions["hot"][subreddit][key]["score"] = []
        submissions["hot"][subreddit][key]["id"] = []
        submissions["hot"][subreddit][key]["url"] = []
        submissions["hot"][subreddit][key]["comms_num"] = []
        submissions["hot"][subreddit][key]["created"] = []
        submissions["hot"][subreddit][key]["body"] = []

        submissions["new"][subreddit][key] = {}
        # new_keyword_object = submissions["new"][subreddit][key]
        submissions["new"][subreddit][key]["title"] = []
        submissions["new"][subreddit][key]["score"] = []
        submissions["new"][subreddit][key]["id"] = []
        submissions["new"][subreddit][key]["url"] = []
        submissions["new"][subreddit][key]["comms_num"] = []
        submissions["new"][subreddit][key]["created"] = []
        submissions["new"][subreddit][key]["body"] = []
        print("Setup keyword", key, " with structure ", submissions)
    print("structure setup for all keywords", submissions)


def setup_structure_for_twitter():
    pass


def setup_structure(source, data):
    if source == "reddit":
        setup_structure_for_subreddit(data["subreddit"], data["keywords_list"])
    elif source == "twitter":
        setup_structure_for_twitter()
