class CampaignParameters:
    def __init__(self, campaign_name, sources, keywords, subreddits):
        self.name = campaign_name
        self.sources = sources
        self.keywords = keywords
        self.subreddits = subreddits

    def __repr__(self):
        return "Campaign name: {0}. Sources: {1}.\nKeywords: {2}.\n Subreddits: {3}.\n".\
            format(self.name, self.sources, self.keywords, self.subreddits)
