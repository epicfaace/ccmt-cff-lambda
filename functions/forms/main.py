import json
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
    headers = {
        'Access-Control-Allow-Origin': '*'
    }
    # if "res" in body and "returnType" in body["res"] and body["res"]["returnType"] == "xlsx":
    #     headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    #     body = body["res"].get("body", "")
    # else:
    body = json.dumps(body, cls=DecimalEncoder)
    return {
        "statusCode": statuscode,
        "headers": headers,
        "body": body,
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
def parseQuery(alias, qs, event):
    if not "action" in qs:
        raise Exception("No query string action provided.")
    if "apiKey" in qs:
        ctrl = FormAdmin(alias, qs['apiKey'])
        if qs["action"] == "formRenderAdmin":
            # render form, plus schema and schemaModifier version list and couponCodes, other form attributes, etc.
            return ctrl.render_form_by_id(qs["id"], qs["version"], True)
        if qs["action"] == "formList":
            return ctrl.list_forms()
        elif qs["action"] == "formResponses":
            return ctrl.get_form_responses(qs["id"], qs["version"], qs.get("format", "json"), qs.get("filter", ""))
        elif qs["action"] == "formEdit":
            return ctrl.edit_form(qs["id"], qs["version"], json.loads(event["body"]))
        #elif qs["action"] == "test":
        #    return ctrl.test()
        else:
            raise Exception("Action not found.")
    else:
        ctrl = FormRender(alias)
        if qs["action"] == "formRender":
            # include_s_sm_versions=true for form editing.
            form = ctrl.render_form_by_id(qs["id"], qs["version"], False)
            if "resid" in qs:
                form["responseLoaded"] = ctrl.get_response(qs["id"], qs["resid"])
            return form
        elif qs["action"] == "schemaGet":
            return ctrl.get_schema(qs["id"], qs["version"])
        elif qs["action"] == "schemaModifierGet":
            return ctrl.get_schemaModifier(qs["id"], qs["version"])
        elif qs["action"] == "formSubmit":
            return ctrl.submit_form(qs["formId"], qs["formVersion"], json.loads(event["body"]), qs.get("modifyLink", ""), qs.get("resid", ""))
        elif qs["action"] == "formSummary": 
            return ctrl.get_response_summary(qs["id"], qs["version"])
        else:
            raise Exception("Action not found.")
    
def handle(event, context):
    alias = event["stageVariables"]["alias"]
    try:
        if not "queryStringParameters" in event or not event["queryStringParameters"]:
            raise Exception("No query string provided.")
        else:
            qs = event["queryStringParameters"]
            if qs["action"] == "ipn":
                handler = IpnHandler(alias)
                results = handler.ipnHandler(event["body"])
                return make_response("", 200)
            results = {"res": parseQuery(alias, qs, event) }
    except Exception:
        results = {"error": True, "message": traceback.format_exc()}
        return make_response(results, 400)
    #if "pathParameters" in event:
    #    results["b"] = event["a"]
    return make_response(results, 200)