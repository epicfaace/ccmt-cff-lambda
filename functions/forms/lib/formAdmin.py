from .dbConnection import DBConnection
from boto3.dynamodb.conditions import Key

class FormAdmin(DBConnection):
    def __init__(self, apiKey):
        super(FormAdmin, self).__init__()
        centers = self.centers.query(
            KeyConditionExpression=Key('apiKey').eq(apiKey)
        )
        if not center or not center["Items"] or not len(center["Items"]):
           raise Exception("Incorrect API Key. No center found for the specified API key.")
        self.centerId = center["Items"][0]["id"]
        if not self.centerId:
           raise Exception("Center found, but no center ID found.")
        self.apiKey = apiKey
    def list_forms(self):
        forms = self.forms.query(
            KeyConditionExpression=Key('center').eq({"id": centerId })
        )
        return forms["Items"]
    def get_form_responses(self, formId, formVersion):
        form = self.forms.get_item(Key={"id": formId, "version": formVersion})["Item"]
        if (form["centerId"] != self.centerId):
            raise Exception("Your center does not have access to this form.")
        responses = self.responses.query(
            KeyConditionExpression=Key('formId').eq(formId)
        )
        return responses["Items"]
    def edit_form(self, formId, formVersion):
        form = self.forms.get_item(Key={"id": formId, "version": formVersion})["Item"]
        if (form["centerId"] != self.centerId):
            raise Exception("Your center does not have access to this form.")
        responses = self.responses.query(
            KeyConditionExpression=Key('form').eq({"id": formId, "version": formVersion })
        )
        return responses["Items"]