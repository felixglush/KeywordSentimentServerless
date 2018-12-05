import boto3
import utils
import constants
import os

s3_client = boto3.resource("s3")

type_id = "ID"
type_text = "TEXT"


class DocumentContainer:
    def __init__(self, doc_type, doc_string):
        self.doc_type = doc_type
        self.doc_string = doc_string


def create_bucket_object(name):
    return s3_client.Bucket(name)


def list_objects(bucket_name):
    bucket = create_bucket_object(bucket_name)
    for obj in bucket.objects.all():
        print(obj.key)


def setup_docs_for_upload(posts):
    ids_list = []
    texts_list = []
    for post in posts:
        texts_list.append(post["title"])
        ids_list.append(post["id"])
        if not utils.is_empty_string(post["body"]):
            texts_list.append(post["body"])
            ids_list.append(post["id"])

    id_string = '\n'.join(ids_list)
    text_string = '\n'.join(texts_list)
    id_container = DocumentContainer(type_id, id_string)
    text_container = DocumentContainer(type_text, text_string)
    return id_container, text_container


def upload_collection(bucket_name, *doc_containers):
    if bucket_name == constants.s3_input_bucket_name:
        for container in doc_containers:
            upload(bucket_name, container)


def upload(bucket_name, doc_container):
    s3_client.Bucket(bucket_name).put_object(Key=doc_container.doc_type, Body=doc_container.doc_string)

