class Parameters:

    # keywords & subreddit are lists
    def __init__(self, keywords, subreddits):
        self.keywords = keywords
        self.subreddits = subreddits

    def set_keywords(self, keywords):
        self.keywords = keywords

    def set_subreddits(self, subreddits):
        self.subreddits = subreddits

    def get_params(self):
        return self.keywords, self.subreddits

