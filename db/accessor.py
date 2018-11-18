import time
import uuid
import boto3

ddb_client = boto3.client('dynamodb', region_name='us-east-1')
ddb_resource = boto3.resource('dynamodb', region_name='us-east-1')

# TODO
# enable stream on campaign table
# specify event source (newly created campaign table) for lambda function which sends new item to frontend


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
        ddb_client.create_table(TableName=table_name,
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


def create_id_for_item():
    id_num = uuid.uuid4()
    return str(id_num)


def put_item(table_name, result):
    print("result to put into ddb", result)
    wait_create_table(table_name, 5, 5)
    table = ddb_resource.Table(table_name)
    id_str = create_id_for_item(table)
    table.put_item(Item={"id": id_str, "result": result})


def wait_create_table(table_name, delay=25, max_attempts=10):
    waiter = ddb_client.get_waiter('table_exists')
    waiter.wait(TableName=table_name,
                WaiterConfig={
                    'Delay': delay,
                    'MaxAttempts': max_attempts
                })
