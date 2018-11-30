import boto3
import utils
import constants
import os

s3_client = boto3.resource("s3")


def create_bucket_object(name):
    return s3_client.Bucket(name)


def list_objects(bucket_name):
    bucket = create_bucket_object(bucket_name)
    for obj in bucket.objects.all():
        print(obj.key)


def setup_files(posts):
    ids_file = open(constants.s3_id_filename, "w+")
    text_file = open(constants.s3_document_filename, "w+")
    for post in posts:
        text_file.write(post["title"])
        ids_file.write(post["id"])
        if not utils.is_empty_string(post["body"]):
            text_file.write(post["body"])
            ids_file.write(post["id"])
    ids_file.close()
    text_file.close()

    return ids_file, text_file


def upload_files(bucket_name, *files):
    if bucket_name == constants.s3_input_bucket:
        for file in files:
            if os.path.basename(file.name) == constants.s3_document_filename:
                upload(bucket_name + constants.s3_bucket_texts, file)
            elif os.path.basename(file.name) == constants.s3_id_filename:
                upload(bucket_name, file)


def upload(bucket_name, file):
    s3_client.meta.client.upload_file(
        Filename=os.path.basename(file.name),
        Bucket=bucket_name,
        Key=os.path.basename(file.name),
    )
