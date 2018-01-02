from bson import json_util
import json
from bson.objectid import ObjectId
from gcmw.formRender import FormRender
from gcmw.formAdmin import FormAdmin

def make_response_success(body):
    return {
        "statusCode": 200,
        "headers": {
            "my_header": "my_value"
        },
        "body": json_util.dumps(body),
        "isBase64Encoded": False
    }
def get_schema(schemaId, version):
    #asd
    pass
def get_schemaModifer(schemaId, version):
    pass
    #asdads
def update_or_create_form(apiKey, schema, schemaModifier, formId=0, version=1):
    # Updates form or creates form.
    pass
def get_form_list(apiKey):
    # asdasd
    pass
def get_responses_for_form(formId):
    #asd
    pass
def parseQuery(qs):
    if (not "action" in qs):
        return {"error": "true"}
    if "apiKey" in qs:
        ctrl = FormAdmin()
        pass
    else:
        ctrl = FormRender()
        if qs["action"] == "getForm":
            return ctrl.render_form_by_id(qs["id"])
        else:
            return {"a":"123"}
    
def lambda_handler(event, context):
    if not "queryStringParameters" in event:
        qs = {}
    else:
        qs = event["queryStringParameters"]
    results = {"res": parseQuery(qs) }
    #if "pathParameters" in event:
    #    results["b"] = event["a"]
    return make_response_success(results)