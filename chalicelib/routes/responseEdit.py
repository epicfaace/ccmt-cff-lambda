import datetime
import re
from chalicelib.models import Response, UpdateTrailItem, PaymentStatusDetailItem, serialize_model
from bson.objectid import ObjectId
from pydash.objects import get, set_
from chalicelib.routes.responseIpnListener import mark_successful_payment
import dateutil

def update_response_path(response, path, value, response_base_path):
    from ..main import app
    existing_value = get(getattr(response, response_base_path), path, value)
    if type(value) is str:
        if type(existing_value) is bool and value.lower() in ("true", "false"):
            value = value.lower() == "true"
        elif type(existing_value) is float and value.isdigit():
            value = float(value)
        elif type(existing_value) is int and value.isdigit():
            value = int(value)
    set_(getattr(response, response_base_path), path, value)
    response.update_trail.append(
        UpdateTrailItem(
            path=path,
            old_value=existing_value,
            new_value=value,
            date=datetime.datetime.now(),
            user=app.get_current_user_id(),
            response_base_path=response_base_path
        )
    )

"""
Edit a response.

JSON body:
1)
{
    path: "participants.0.age"
    value: 12,
    responseBasePath: "value"
}

2)
{
    responseBasePath: "value",
    batch: [
        {
            path: "participants.0.checkin",
            value: true
        },
        {
            path: "participants.1.checkin",
            value: true
        }
    ]
}


"""

def response_edit_common(responseId, response_base_path):
    from ..main import app
    response = Response.objects.get({"_id": ObjectId(responseId)})
    path = app.current_request.json_body.get("path", None)
    value = app.current_request.json_body.get("value", None)
    batch = app.current_request.json_body.get("batch", None)
    if batch is None:
        batch = [{"path": path, "value": value}]
    if response_base_path == "value":
        if all(item["path"].endswith(".checkin") for item in batch):
            app.check_permissions(response.form, ["Responses_CheckIn", "Responses_Edit"])
        else:
            app.check_permissions(response.form, "Responses_Edit")
    elif response_base_path == "admin_info":
        app.check_permissions(response.form, "Responses_AdminInfo_Edit")
    else:
        raise Exception("response_base_path specified is not valid or you not have permissions to perform the specified action.")
    for item in batch:
        update_response_path(response, item["path"], item["value"], response_base_path)
    response.save()
    return {"res": {"success": True, "response": serialize_model(response)}}

def response_edit_value(responseId):
    return response_edit_common(responseId, "value")

def response_edit_admin_info(responseId):
    return response_edit_common(responseId, "admin_info")

def response_checkin(formId, responseId):
    pass

def response_payment(responseId):
    from ..main import app
    response = Response.objects.get({"_id": ObjectId(responseId)})
    app.check_permissions(response.form, "Responses_Edit")
    amount = app.current_request.json_body["amount"]
    currency = app.current_request.json_body["currency"]
    date = app.current_request.json_body.get("date", None)
    if date and "$date" in date:
        date = dateutil.parser.parse(date["$date"])
    id = app.current_request.json_body["id"]
    method = app.current_request.json_body["method"]
    send_email = app.current_request.json_body.get("sendEmail", True)
    paid = mark_successful_payment(response.form, response, {"type": "manual", "method": method, "id": id}, method, amount, currency, id, date=date, send_email=send_email)
    response.save()
    return {"res": {"success": True, "paid": paid, "response": serialize_model(response)}}

def response_delete(responseId):
    from ..main import app
    response = Response.objects.get({"_id": ObjectId(responseId)})
    app.check_permissions(response.form, "Responses_Delete")
    response.delete()
    return {"res": {"success": True, "response": serialize_model(response)}}