from decimal import Decimal


def convert_to_decimal(sentiment_score):
    sentiment_score["Positive"] = Decimal(sentiment_score["Positive"])
    sentiment_score["Negative"] = Decimal(sentiment_score["Negative"])
    sentiment_score["Neutral"] = Decimal(sentiment_score["Neutral"])
    sentiment_score["Mixed"] = Decimal(sentiment_score["Mixed"])
    return sentiment_score
