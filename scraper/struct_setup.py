submissions = {"hot": {}, "new": {}}
analysis_results = {}


def setup_structure_for_subreddit(subreddit, keywords_list):
    submissions["hot"][subreddit] = {}
    submissions["new"][subreddit] = {}
    for key in keywords_list:
        print("setting up keyword", key)
        submissions["hot"][subreddit][key] = {}
        submissions["hot"][subreddit][key]["posts"] = []

        submissions["new"][subreddit][key] = {}
        submissions["new"][subreddit][key]["posts"] = []
        print("Setup keyword", key, " with structure ", submissions)
    print("structure setup for all keywords", submissions)


def setup_structure(source, data):
    if source == "reddit":
        setup_structure_for_subreddit(data["subreddit"], data["keywords_list"])
