import time
import uuid
import boto3

ddb_client = boto3.client('dynamodb', region_name='us-east-1')
ddb_resource = boto3.resource('dynamodb', region_name='us-east-1')


def table_exists(table_name):
    response = ddb_client.list_tables()
    print("list of tables", response)
    table_names = response["TableNames"]  # an array
    if table_name not in table_names:
        return False
    else:
        return True


def create_table(table_name):
    if not table_exists(table_name):
        print("creating table", table_name)
        ddb_client.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            },
        )


def delete_table_when_active(table_name):
    table = ddb_resource.Table(table_name)
    table_status = table.status
    if table_status == "ACTIVE":
        table.delete()
    elif table_status == "UPDATING":
        time.sleep(5)
        delete_table_when_active(table_name)


def delete_table(table_name):
    print("deleting table", table_name)
    wait_create_table(table_name, 5, 5)  # Delete when active
    delete_table_when_active(table_name)  # Cannot delete when table is updating, so make sure it is not


def put_item(table_name, item):
    print("result to put into ddb", item)
    wait_create_table(table_name, 5, 5)
    table = ddb_resource.Table(table_name)
    id_str = create_id_for_item()
    table.put_item(Item={"id": id_str, "item": item})


def batch_put_ids(post_ids, table_name):
    table = ddb_resource.Table(table_name)
    with table.batch_writer() as batch:
        for post_id in post_ids:
            batch.put_item(Item={"id": post_id})


def batch_put_posts(posts, source):
    table = ddb_resource.Table("Posts")
    with table.batch_writer() as batch:
        for post in posts:
            analyzed = post["sentiment"] is not None
            batch.put_item(
                Item={
                    "PostId": post["id"],
                    "Post": post,
                    "Source": source,
                    "IsAnalyzed": analyzed,
                }
            )


def wait_create_table(table_name, delay=25, max_attempts=10):
    waiter = ddb_client.get_waiter('table_exists')
    waiter.wait(TableName=table_name,
                WaiterConfig={
                    'Delay': delay,
                    'MaxAttempts': max_attempts
                })


def create_id_for_item():
    return str(uuid.uuid4())
