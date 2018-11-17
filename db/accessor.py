import time

import boto3

dynamodb = boto3.client('dynamodb', region_name='us-east-1')


def table_exists(table_name):
    response = dynamodb.list_tables()
    print("list of tables", response)
    table_names = response["TableNames"]  # an array
    if table_name not in table_names:
        return False
    else:
        return True


def create_table(table_name):
    if not table_exists(table_name):
        print("creating table", table_name)
        dynamodb.create_table(TableName=table_name,
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
    response = dynamodb.describe_table(TableName=table_name)
    table_status = response["Table"]["TableStatus"]
    if table_status == "ACTIVE":
        dynamodb.delete_table(TableName=table_name)
    elif table_status == "UPDATING":
        time.sleep(5)
        delete_table_when_active(table_name)


def delete_table(table_name):
    print("deleting table", table_name)
    wait_create_table(table_name, 5, 5)   # Delete when active
    delete_table_when_active(table_name)  # Cannot delete when table is updating, so make sure it is not


def put_item(table_name, result):
    wait_create_table(table_name, 5, 5)
    dynamodb.put_item(
        TableName=table_name,
        Item={
            "id": {'N': "1"},
        })


def wait_create_table(table_name, delay=25, max_attempts=10):
    waiter = dynamodb.get_waiter('table_exists')
    waiter.wait(TableName=table_name,
                WaiterConfig={
                    'Delay': delay,
                    'MaxAttempts': max_attempts
                })
