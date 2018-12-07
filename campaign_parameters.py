class CampaignParameters:
    def __init__(self, campaign_name, sources, keywords, subreddits):
        self.name = campaign_name
        self.sources = sources
        self.keywords = keywords
        self.subreddits = subreddits

    def __repr__(self):
        return "Campaign name: {0}. Sources: {1}.Keywords: {2}. Subreddits: {3}.".\
            format(self.name, self.sources, self.keywords, self.subreddits)
