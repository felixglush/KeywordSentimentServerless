import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')


def create_table(table_name):
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
