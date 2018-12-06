s3_input_bucket_name = "keyword-tracker-analysis-input"
s3_output_bucket_name = "keyword-tracker-analysis-output"
s3_input_bucket_uri = 's3://' + s3_input_bucket_name
s3_output_bucket_uri = 's3://' + s3_output_bucket_name
s3_bucket_texts = '/lines'
s3_data_access_role_arn = 'arn:aws:iam::433181616955:role/S3DataAccessRoleForComprehend'
s3_comprehend_sentiment_detection_job_name = 'KeywordSentimentDetectionJob'

sleep_time_for_campaign_poll = 60  # seconds
type_id = "ID"
type_text = "TEXT"