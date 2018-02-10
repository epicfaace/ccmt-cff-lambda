#!/usr/bin/env python3

""" Copy an AWS dynamodb table to an existing table with an exponential timing back-off
    Assume receiving table has a compatible schema
"""

import logging
from time import sleep
import boto3
from botocore.exceptions import ClientError

client = boto3.client('dynamodb')

def handle(event, context):
    tableNames = ["forms", "centers", "schemas", "schemaModifiers", "responses"]
    fromStage = "dev"
    toStage = "beta"
    for tableName in tableNames:
        fromName = "cff_{}.{}".format(fromStage, tableName)
        toName = "cff_{}.{}".format(toStage, tableName)
        backup = client.create_backup(
            TableName=fromName,
            BackupName=fromName
        )
        try:
            client.restore_table_from_backup(
                TargetTableName=toName,
                BackupArn=backup['BackupDetails']['BackupArn']
            )
        except ClientError as ce:
            if ce.response['Error']['Code'] == 'TableAlreadyExistsException':
                """client.delete_table(TableName=toName)
                client.restore_table_from_backup(
                    TargetTableName=toName,
                    BackupArn=backup['BackupDetails']['BackupArn']
                )"""
            else:
                raise ce