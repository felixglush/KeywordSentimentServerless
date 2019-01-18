# KeywordSentimentServerless

An AWS Lambda application that scrapes social media websites for keywords and performs sentiment analysis using Amazon Comprehend on the text containing the keywords.

# Definitions
**Campaign**: A collection of campaign name, keywords, subreddits to search, and social media websites to search.

# Architecture

**Lambda Functions**:
- processCampaignTableStream: triggers scrapeReddit
- processPostsTableStream: parses the Posts table stream, analyzing posts
- scrapeReddit: queries reddit using PRAW, then filters posts by Campaign parameters
- searchElastic: given a query, searches Elasticsearch

**DynamoDB Tables**:
- Campaigns
- Posts

**Elasticsearch indices**:
- posts

A DynamoDB Stream is enabled on the Campaigns and Posts tables. Posting to those tables triggers the AWS Lambda functions processCampaignTableStream and processPostsTableStream, respectively. processCampaignTableStream triggers Lambda function scrapeReddit which sends posts matching parameters specified by the Campaign to the Posts table. Then those posts are streamed to processPostsTableStream where they are analyzed by Amazon Comprehend and indexed into Amazon Elasticsearch.

# Future Possibilities
Now that the posts are indexed into Elasticsearch, temporal tracking of negative posts and data analysis & visualization of posts are useful applications for 1) brands interested in sentiment surrounding their products and services and 2) studies relating to the sentiment around controversial topics. Tracking a post through time can be implemented by adding a "retrieved on" attribute to the post data and by creating a CloudWatch rule that periodically queries and analyzes each post in the Elasticsearch index.

Furthermore, Twitter search can be integrated into the application.
