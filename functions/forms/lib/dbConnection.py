import boto3

client = boto3.client('dynamodb')
class DBConnection(object):
    def __init__(self):
        self.client = client
        self.db = None