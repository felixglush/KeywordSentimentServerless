import json
from io import BytesIO

import boto3
import utils
import constants
from constants import type_id, type_text
import tarfile

s3_resource = boto3.resource("s3")


class DocumentContainer:
    # Metadata: campaign name
    def __init__(self, doc_type, doc_string, metadata=None):
        self.doc_type = doc_type
        self.doc_string = doc_string
        self.metadata = metadata


def list_objects(bucket_name):
    bucket = s3_resource.Bucket(bucket_name)
    for obj in bucket.objects.all():
        print(obj.key)


def setup_docs_for_upload(posts, metadata={}):
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
    id_container = DocumentContainer(type_id, id_string, metadata)
    text_container = DocumentContainer(type_text, text_string)
    return id_container, text_container


def upload_collection(bucket_name, *doc_containers):
    if bucket_name == constants.s3_input_bucket_name:
        for container in doc_containers:
            upload(bucket_name, container)


def upload(bucket_name, doc_container):
    list_objects(constants.s3_output_bucket_name)
    in_bucket = s3_resource.Bucket(bucket_name)
    in_bucket.put_object(Key=doc_container.doc_type, Body=doc_container.doc_string)
    if doc_container.doc_type == type_id:
        out_bucket = s3_resource.Bucket(constants.s3_output_bucket_name)
        out_bucket.put_object(Key=doc_container.doc_type,
                              Body=doc_container.doc_string,
                              Metadata=doc_container.metadata)


def get_object(bucket_name, key):
    key = "433181616955-SENTIMENT-6ec49c899f5dbb077b7d8e8cfef8a814/output/output.tar.gz"
    obj = s3_resource.Object(bucket_name, key)
    print("Object key", key, obj)
    content = read_targz_contents(obj.get()["Body"].read())


def read_targz_contents(targz_bytes):
    bytestream = BytesIO(targz_bytes)
    with tarfile.open(fileobj=bytestream) as targz:
        for member in targz.getmembers():
            f = targz.extractfile(member)
            content = f.read().decode("utf-8")
            splitlist = content.split("\n")
            # lines = [line.rstrip('\n') for line in f.read()]
            # print("lines", lines)
            return splitlist
