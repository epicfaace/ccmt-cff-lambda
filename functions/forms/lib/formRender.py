from .dbConnection import DBConnection
from .util import calculate_price
from .responseHandler import response_verify_update
import datetime
import uuid
from decimal import Decimal
from boto3.dynamodb.conditions import Key
# Ref:
# https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GettingStarted.Python.03.html

class FormRender(DBConnection):
    def render_form_by_id(self, formId, formVersion, include_s_sm_versions):
        """Renders form with its schema and uiSchema resolved.
        """
        form = self.get_form(formId, formVersion)
        self.set_form_schemas(form)
        if include_s_sm_versions:
            # used when editing the form.
            form['schema_versions'] = self.get_versions(self.schemas, form['schema']['id'])
            form['schemaModifier_versions'] = self.get_versions(self.schemaModifiers, form['schemaModifier']['id'])
        return form
    def get_response(self, formId, responseId):
        """Renders response; used when editing a form."""
        response = self.responses.get_item(Key={"formId": formId, "responseId": responseId})["Item"]
        return response
    def set_form_schemas(self, form):
        """Renders form with its schema and uiSchema resolved.
        """
        form['schema'] = self.schemas.get_item(Key=form['schema'])["Item"]
        form['schemaModifier'] = self.schemaModifiers.get_item(Key=form['schemaModifier'])["Item"]
        return form
    def get_latest_version(self, collection, id):
        return self.get_versions(collection, id, 1)[0]["version"]
    def get_versions(self, collection, id, limit = None):
        kwargs = {
            "KeyConditionExpression":Key('id').eq(id),
            "ProjectionExpression":"version, date_created, date_last_modified",
            "ScanIndexForward":False # sort in descending order.
        }
        if limit:
            kwargs["Limit"] = limit
        return collection.query(**kwargs)['Items']
    def get_form(self, id, version):
        return self.forms.get_item(Key={"id": id, "version": int(version)})["Item"]
    def get_schema(self, id, version):
        return self.schemas.get_item(Key={"id": id, "version": int(version)})["Item"]
    def get_schemaModifier(self, id, version):
        return self.schemaModifiers.get_item(Key={"id": id, "version": int(version)})["Item"]
    def submit_form(self, formId, formVersion, response_data, modifyLink, responseId):
        form = self.get_form(formId, formVersion)
        schemaModifier = self.schemaModifiers.get_item(Key=form['schemaModifier'])['Item']
        paymentInfo = schemaModifier['paymentInfo']

        paymentInfo['total'] = 0
        for paymentInfoItem in paymentInfo['items']:
            paymentInfoItem['amount'] = Decimal(calculate_price(paymentInfoItem.get('amount', '0'), response_data))
            paymentInfoItem['quantity'] = Decimal(calculate_price(paymentInfoItem.get('quantity', '0'), response_data))
            paymentInfo['total'] += paymentInfoItem['amount'] * paymentInfoItem['quantity']
        paymentInfo['items'] = [item for item in paymentInfo['items'] if item['quantity'] * item['amount'] != 0]
        
        if not responseId:
            responseId = str(uuid.uuid4())
            self.responses.put_item(
                Item={
                    "formId": formId, # partition key
                    "responseId": responseId, # sort key
                    "modifyLink": modifyLink,
                    "value": response_data,
                    "date_last_modified": datetime.datetime.now().isoformat(),
                    "date_created": datetime.datetime.now().isoformat(),
                    "form": {
                            'id': formId,
                            'version': formVersion
                    }, # id, version.
                    "paymentInfo": paymentInfo,
                    "confirmationEmailInfo": schemaModifier['confirmationEmailInfo'],
                    "PAID": False
            })
            return {"success": True, "action": "insert", "id": responseId, "paymentInfo": paymentInfo }
        else:
            response_old = self.responses.get_item(Key={ 'formId': formId, 'responseId': responseId })["Item"]
            response_new = self.responses.update_item(
                Key={ 'formId': formId, 'responseId': responseId },
                UpdateExpression=("SET"
                    " UPDATE_HISTORY = list_append(if_not_exists(UPDATE_HISTORY, :empty_list), :updateHistory),"
                    " PENDING_UPDATE = :pendingUpdate,"
                    " date_last_modified = :now"),
                ExpressionAttributeValues={
                    ':updateHistory': [{
                        "date": datetime.datetime.now().isoformat(),
                        "action": "pending_update"
                    }],
                    ":pendingUpdate": {
                        "value": response_data,
                        "modifyLink": modifyLink,
                        "paymentInfo": paymentInfo
                    },
                    ':empty_list': [],
                    ":now": datetime.datetime.now().isoformat()
                },
                # todo: if not updated, do this ...
                ReturnValues="ALL_NEW"
                )["Attributes"]
            if response_old.get("PAID", None) == True and paymentInfo["total"] <= response_old["paymentInfo"]["total"]:
                response_verify_update(response_new, self.responses)
            return {
                "success": True,
                "action": "update",
                "id": responseId,
                "paymentInfo": paymentInfo,
                "total_amt_received": response_old.get("IPN_TOTAL_AMOUNT", 0), # todo: encode currency into here as well.
                "paymentInfo_old": response_old["paymentInfo"]
            }