import boto3
import os

dynamodb = boto3.resource('dynamodb')

possiblePrefixes = {
    "DEV": "cff_dev",
    "BETA": "cff_beta",
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
        #self.user_permissions = dynamodb.Table(prefix + ".user_permissions")
        self.schemas = dynamodb.Table(prefix + ".schemas")
