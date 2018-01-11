import json
from bson.objectid import ObjectId
from lib.formRender import FormRender
from lib.formAdmin import FormAdmin
from lib.ipnHandler import IpnHandler
import traceback
import decimal


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)

def make_response(body, statuscode):
    return {
        "statusCode": statuscode,
        "headers": {
            'Access-Control-Allow-Origin': '*'
        },
        "body": json.dumps(body, cls=DecimalEncoder),
        "isBase64Encoded": False
    }
def get_schema(schemaId, version):
    #asd
    pass
def get_schemaModifier(schemaId, version):
    pass
    #asdads
def update_or_create_form(apiKey, schema, schemaModifier, formId=0, version=1):
    # Updates form or creates form.
    pass
def parseQuery(qs, event):
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
            return ctrl.render_form_by_id(qs["id"], qs["version"])
        if qs["action"] == "getResponseAndSchemas":
            return ctrl.render_response_and_schemas(qs["id"])
        elif qs["action"] == "formSubmit":
            return ctrl.submit_form(qs["formId"], qs["formVersion"], json.loads(event["body"]), qs.get("modifyLink", ""))
        elif qs["action"] == "formResponseEdit":
            return ctrl.edit_response_form(qs["id"], json.loads(event["body"]))
        else:
            raise Exception("Action not found.")
    
def handle(event, context):
    try:
        if not "queryStringParameters" in event or not event["queryStringParameters"]:
            raise Exception("No query string provided.")
        else:
            qs = event["queryStringParameters"]
            if qs["action"] == "ipn":
                handler = IpnHandler()
                results = handler.ipnHandler(event["body"])
                return make_response("", 200)
            results = {"res": parseQuery(qs, event) }
    except Exception:
        results = {"error": True, "message": traceback.format_exc()}
        return make_response(results, 400)
    #if "pathParameters" in event:
    #    results["b"] = event["a"]
    return make_response(results, 200)