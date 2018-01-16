from .dbConnection import DBConnection
from boto3.dynamodb.conditions import Key

class FormAdmin(DBConnection):
    def __init__(self, alias, apiKey):
        super(FormAdmin, self).__init__(alias)
        center = self.centers.get_item(Key={"apiKey": apiKey})["Item"]
        if not center:
           raise Exception("Incorrect API Key. No center found for the specified API key.")
        self.centerId = center["id"]
        if not self.centerId:
           raise Exception("Center found, but no center ID found.")
        self.apiKey = apiKey
    def list_forms(self):
        forms = self.forms.query(
            IndexName='center-index',
#           KeyConditionExpression=Key('center').eq(self.centerId)
            KeyConditionExpression='center = :c',
            ExpressionAttributeValues={ ':c': self.centerId} 
        )
        return forms["Items"]
    def get_form_responses(self, formId, formVersion):
        form = self.forms.get_item(Key={"id": formId, "version": int(formVersion)})["Item"]
        if (form["center"] != self.centerId):
            raise Exception("Your center does not have access to this form.")
        responses = self.responses.query(
            KeyConditionExpression=Key('formId').eq(formId)
        )
        return responses["Items"]
    def edit_form(self, formId, formVersion):
        pass