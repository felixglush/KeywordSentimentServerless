import scraper
import sentimenter


# See the *_scratch.json files for the submissions and analysis_results structure templates

def run():
    keywords_list = ["The"]
    subreddits_list = ["uwaterloo"]
    sources = ["reddit"]

    # Scrape the data from sources
    reddit = scraper.init_reddit_scraper()
    submissions, analysis_results = scraper.scrape_submissions_from_subreddits(reddit, subreddits_list, keywords_list)
    analysis_results["sources"] = sources
    analysis_results["keywords"] = keywords_list

    # Analyze the text
    # (desired) side effect: analysis_results will be modified
    sentimenter.analyze(submissions, analysis_results)

    print("submissions", submissions)
    print("analysis_results", analysis_results)
    return analysis_results


run()