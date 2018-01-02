from bson import json_util
import json
from bson.objectid import ObjectId
from lib.formRender import FormRender
from lib.formAdmin import FormAdmin

def make_response(body, statuscode):
    return {
        "statusCode": statuscode,
        "headers": {
            'Access-Control-Allow-Origin': '*'
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
    if not "action" in qs:
        raise Exception("No query string action provided.")
    if "apiKey" in qs:
        ctrl = FormAdmin(qs['apiKey'])
        if qs["action"] == "formList":
            return ctrl.list_forms()
        elif qs["action"] == "formResponses":
            return ctrl.get_form_responses(qs["id"])
        else:
            raise Exception("Action not found.")
    else:
        ctrl = FormRender()
        if qs["action"] == "formRender":
            return ctrl.render_form_by_id(qs["id"])
        else:
            raise Exception("Action not found.")
    
def handle(event, context):
    try:
        if not "queryStringParameters" in event or not event["queryStringParameters"]:
            raise Exception("No query string provided.")
        else:
            qs = event["queryStringParameters"]
            results = {"res": parseQuery(qs) }
    except Exception as e:
        results = {"error": True, "message": e.__str__()}
        return make_response(results, 400)
    #if "pathParameters" in event:
    #    results["b"] = event["a"]
    return make_response(results, 200)