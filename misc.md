from botocore.exceptions import ClientError

except ClientError as e:
    # Ignore the ConditionalCheckFailedException, bubble up
    # other exceptions.
    if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
        raise