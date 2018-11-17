# KeywordSentimentServerless

An AWS Lambda application that scrapes social media websites for keywords and performs sentiment analysis using Amazon Comprehend on the text containing the keywords.

Contains two AWS Lambda functions:
* source scraping function
* a function that is triggered by additions to the Campaigns table in DynamoDB, which creates a table for the individual campaign

Sources currently supported:
* reddit

In the works:
* twitter
* yelp
