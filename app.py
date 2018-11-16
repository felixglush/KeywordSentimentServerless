from scraper import scraper
from scraper import sentimenter
from db import accessor as ddb

# See the *_scratch.json files for the submissions and analysis_results structure templates


def run_scraper(query_parameters):
    print("running")
    sources = query_parameters["sources"]
    keywords_list = query_parameters["keywords_list"]
    subreddits_list = []
    if "reddit" in sources:
        subreddits_list = query_parameters["subreddits_list"]

    # Scrape the data from sources
    print("scraping")
    reddit = scraper.init_reddit_scraper()
    submissions, analysis_results = scraper.scrape_submissions_from_subreddits(reddit, subreddits_list, keywords_list)
    analysis_results["sources"] = sources
    analysis_results["keywords"] = keywords_list

    # Analyze the text
    # (desired) side effect: analysis_results will be modified
    print("analyzing sentiment")
    sentimenter.analyze(submissions, analysis_results)

    print("submissions", submissions)
    print("analysis_results", analysis_results)
    return analysis_results


mock_params = {
    "keywords_list": ["the"],
    "subreddits_list": ["uwaterloo"],
    "sources": ["reddit"]
}

# run_scraper(mock_params)


def run_create_table(info):
    print("run_create_table with info ", info)
    table_name = info["Keys"]["CampaignName"]["S"].replace(" ", "")
    ddb.create_table(table_name)

    # call run_scraper
    # put returned data into table
