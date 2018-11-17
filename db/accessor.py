import time

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
                                      'AttributeType': 'N'
                                  },
                              ],
                                ProvisionedThroughput={
                                  'ReadCapacityUnits': 10,
                                  'WriteCapacityUnits': 10
                              }
                                )


def delete_table_when_active(table_name):
    response = ddb_client.describe_table(TableName=table_name)
    table_status = response["Table"]["TableStatus"]
    if table_status == "ACTIVE":
        ddb_client.delete_table(TableName=table_name)
    elif table_status == "UPDATING":
        time.sleep(5)
        delete_table_when_active(table_name)


def delete_table(table_name):
    print("deleting table", table_name)
    wait_create_table(table_name, 5, 5)  # Delete when active
    delete_table_when_active(table_name)  # Cannot delete when table is updating, so make sure it is not


def create_id_for_item(table):
    id_num = table.item_count + 1
    return id_num


def put_item(table_name, result):
    print("result to put into ddb", result)
    wait_create_table(table_name, 5, 5)
    table = ddb_resource.Table(table_name)
    id_num = create_id_for_item(table)
    table.put_item(Item={"id": id_num, "result": result})


def wait_create_table(table_name, delay=25, max_attempts=10):
    waiter = ddb_client.get_waiter('table_exists')
    waiter.wait(TableName=table_name,
                WaiterConfig={
                    'Delay': delay,
                    'MaxAttempts': max_attempts
                })
