import parameters


class Model:
    def __init__(self):
        self.params = parameters.Parameters(None, None)
        self.submissions = {"hot": {}, "new": {}}

    def set_params(self, keywords, subreddits):
        self.params.set_keywords(keywords)
        self.params.set_subreddits(subreddits)

    def get_params(self):
        return self.params

    def set_submissions(self, submissions):
        self.submissions = submissions

    def get_submissions(self):
        return self.submissions


