import boto3
s3_client = boto3.resource("s3")


def create_bucket_object(name):
    return s3_client.Bucket(name)


def list_objects(bucket_name):
    bucket = create_bucket_object(bucket_name)
    for obj in bucket.objects.all():
        print(obj.key)


def put_object_into_bucket(object, bucket_name):
    pass

