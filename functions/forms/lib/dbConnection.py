import boto3

dynamodb = boto3.resource('dynamodb')
class DBConnection(object):
    def __init__(self):
        self.dynamodb = dynamodb
        self.db = None
        self.responses = dynamodb.Table("ccmt_cff_responses")
        self.schemaModifiers = dynamodb.Table("ccmt_cff_schemaModifiers")
        self.forms = dynamodb.Table("ccmt_cff_forms")
        self.centers = dynamodb.Table("ccmt_cff_centers")
        self.schemas = dynamodb.Table("ccmt_cff_schemas")