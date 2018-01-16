import boto3
import os

dynamodb = boto3.resource('dynamodb')

possiblePrefixes = {
    "DEV": "cff_dev",
    "PROD": "cff_prod"
}

class DBConnection(object):
    def __init__(self, alias):
        self.dynamodb = dynamodb
        self.alias = alias
        prefix = possiblePrefixes[alias]
        self.responses = dynamodb.Table(prefix + ".responses")
        self.schemaModifiers = dynamodb.Table(prefix + ".schemaModifiers")
        self.forms = dynamodb.Table(prefix + ".forms")
        self.centers = dynamodb.Table(prefix + ".centers")
        self.schemas = dynamodb.Table(prefix + ".schemas")