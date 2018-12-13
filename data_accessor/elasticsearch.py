from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3

# For example, my-test-domain.us-east-1.es.amazonaws.com
host = "search-keyword-tracker-sp4elblt3jbsvk7nzaae3bg6qu.us-east-1.es.amazonaws.com"
region = "us-east-1"

service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service)

es = Elasticsearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)


def index(es_index, doc_type, es_id, body):
    es.index(index=es_index, doc_type=doc_type, id=es_id, body=body)


def get(es_index, doc_type, es_id):
    return es.get(index=es_index, doc_type=doc_type, id=es_id)


def bulk_index():
    pass


def search():
    pass