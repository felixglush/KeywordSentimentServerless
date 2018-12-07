class RedditPost:
    def __init__(self, title, post_id, subreddit, score, url, num_comments, date, filters, body=None):
        self.title = title
        self.body = body
        self.post_id = post_id
        self.subreddit = subreddit
        self.score = score
        self.url = url
        self.num_comments = num_comments
        self.date = date
        self.filters = filters

    def __repr__(self):
        return self.__dict__


class TwitterPost:
    def __init__(self, text, post_id, date, user_screen_name, truncated):
        self.text = text
        self.post_id = post_id
        self.date = date
        self.user_screen_name = user_screen_name
        self.truncated = truncated

    def __repr__(self):
        return self.__dict__