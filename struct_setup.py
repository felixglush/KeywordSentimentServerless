

submissions = {"hot": {}, "new": {}}
analysis_results = {}


def setup_structure_for_subreddit(subreddit, keywords_list):
    analysis_results["reddit"] = {}
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

        submissions["hot"][subreddit] = {}
        submissions["hot"][subreddit][key] = {}
        hot_keyword_object = submissions["hot"][subreddit][key]
        hot_keyword_object["title"] = []
        hot_keyword_object["score"] = []
        hot_keyword_object["id"] = []
        hot_keyword_object["url"] = []
        hot_keyword_object["comms_num"] = []
        hot_keyword_object["created"] = []
        hot_keyword_object["body"] = []

        submissions["new"][subreddit] = {}
        submissions["new"][subreddit][key] = {}
        new_keyword_object = submissions["new"][subreddit][key]
        new_keyword_object["title"] = []
        new_keyword_object["score"] = []
        new_keyword_object["id"] = []
        new_keyword_object["url"] = []
        new_keyword_object["comms_num"] = []
        new_keyword_object["created"] = []
        new_keyword_object["body"] = []


def setup_structure_for_twitter():
    pass


def setup_structure(source, data):
    if source == "reddit":
        setup_structure_for_subreddit(data["subreddit"], data["keywords_list"])
    elif source == "twitter":
        setup_structure_for_twitter()
