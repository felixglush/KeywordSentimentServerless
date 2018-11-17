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


def put_item(table_name, result):
    waiter = dynamodb.get_waiter('table_exists')
    waiter.wait(TableName=table_name,
                WaiterConfig={
                    'Delay': 5,
                    'MaxAttempts': 11
                })
    dynamodb.put_item(
        TableName=table_name,
        Item={
            "id": {'N': "1"},
        })
