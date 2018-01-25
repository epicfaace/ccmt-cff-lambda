from .formRender import FormRender
import datetime
from boto3.dynamodb.conditions import Key

def pickIdVersion(dict):
    # picks the ID and version from a dictionary.
    return { k: dict[k] for k in ["id", "version"] }

class FormAdmin(FormRender):
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
    def update_form_entry(self, formId, formVersion, body):
        # Helper function.
        formKey = {"id": formId, "version": int(formVersion)}
        form = self.forms.get_item(Key=formKey)["Item"]
        formUpdateExpression = []
        formExpressionAttributeValues = {}
        formExpressionAttributeNames = {}
        if "schema" in body and body["schema"]["version"] != form["schema"]["version"]:
            # schema is a reserved keyword
            formUpdateExpression.append("#schema = :s")
            formExpressionAttributeNames["#schema"] = "schema"
            formExpressionAttributeValues[":s"] = pickIdVersion(body["schema"])
        if "schemaModifier" in body and body["schemaModifier"] != form["schemaModifier"]:
            formUpdateExpression.append("schemaModifier = :sm")
            formExpressionAttributeValues[":sm"] = pickIdVersion(body["schemaModifier"])
        #if "center" in body:
        #    formUpdateExpression.append("center = :c")
        #    formExpressionAttributeValues[":c"] = body["center"]
        if "name" in body:
            # name is a reserved keyword so need to do it this way:
            formUpdateExpression.append("#name = :n")
            formExpressionAttributeNames["#name"] = "name"
            formExpressionAttributeValues[":n"] = body["name"]
        formUpdateExpression.append("date_last_modified = :now")
        formExpressionAttributeValues[":now"] = datetime.datetime.now().isoformat()
        if len(formUpdateExpression) == 0:
            raise Exception("Nothing to update.")
        return self.forms.update_item(
            Key=formKey,
            UpdateExpression= "SET " + ",".join(formUpdateExpression),
            ExpressionAttributeValues=formExpressionAttributeValues,
            ExpressionAttributeNames=formExpressionAttributeNames,
            ReturnValues="UPDATED_NEW"
        )["Attributes"]
    def upsert_s_or_sm_entry(self, collection, data):
        # Helper function. Puts (replaces) item; increments version # if # is "NEW".
        if data["version"] == "NEW":
            data["version"] = self.get_latest_version(collection, data["id"]) + 1
            data["date_created"] = datetime.datetime.now().isoformat()
        data["date_last_modified"] = datetime.datetime.now().isoformat()
        collection.put_item(
            Item=data
        )
        return data
    def edit_form(self, formId, formVersion, body):
        if "schema" in body:
            body["schema"] = self.upsert_s_or_sm_entry(self.schemas, body["schema"])
        if "schemaModifier" in body:
            body["schemaModifier"] = self.upsert_s_or_sm_entry(self.schemaModifiers, body["schemaModifier"])
        body["form"] = self.update_form_entry(formId, formVersion, body)
        body['schema_versions'] = self.get_versions(self.schemas, body['schema']['id'])
        body['schemaModifier_versions'] = self.get_versions(self.schemaModifiers, body['schemaModifier']['id'])
        return {
            "success": True,
            "updated_values": body
        }