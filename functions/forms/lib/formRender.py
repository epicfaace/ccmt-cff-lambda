from .dbConnection import DBConnection
from .util import calculate_price
from .responseHandler import response_verify_update
import datetime
import uuid
from decimal import Decimal
# Ref:
# https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GettingStarted.Python.03.html

class FormRender(DBConnection):
    def render_form_by_id(self, formId, formVersion):
        """Renders form with its schema and uiSchema resolved.
        """
        form = self.get_form(formId, formVersion)
        self.set_form_schemas(form)
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
    def get_form(self, id, version):
        return self.forms.get_item(Key={"id": id, "version": int(version)})["Item"]
    def get_schema(self, id, version):
        return self.schemas.get_item(Key={"id": id, "version": int(version)})["Item"]
    def get_schemaModifier(self, id, version):
        return self.schemaModifiers.get_item(Key={"id": id, "version": int(version)})["Item"]
    def update_form(self, id, version, schemaId, schemaModifierId):
        # Not used (yet).
        return self.forms.update_item(
            Key={
                'id': str(id),
                'version': int(version)
            },
            UpdateExpression="set schema = :s, schemaModifier =:sm",
            ExpressionAttributeValues={
                ':s': schemaId,
                ':sm': schemaModifierId
            },
            ReturnValues="UPDATED_NEW"
        )
    def submit_form(self, formId, formVersion, response_data, modifyLink, responseId):
        form = self.get_form(formId, formVersion)
        schemaModifier = self.schemaModifiers.get_item(Key=form['schemaModifier'])['Item']
        paymentInfo = schemaModifier['paymentInfo']
        paymentInfo['total'] = Decimal(calculate_price(paymentInfo['total'], response_data))
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
            response_old = self.responses.update_item(
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
                ReturnValues="ALL_OLD"
                )["Attributes"]
            if response_old.get("PAID", None) == True and paymentInfo["total"] >= response_old["PENDING_UPDATE"]["paymentInfo"]["total"]:
                response_verify_update(response, self.responses)
            return {
                "success": True,
                "action": "update",
                "id": responseId,
                "paymentInfo": paymentInfo,
                "total_amt_received": response_old.get("IPN_TOTAL_AMOUNT", 0), # todo: encode currency into here as well.
                "paymentInfo_old": response_old["paymentInfo"]
            }