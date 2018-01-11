from .dbConnection import DBConnection
from bson import ObjectId
import datetime
# Ref:
# https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GettingStarted.Python.03.html

class FormRender(DBConnection):
    def render_form_by_id(self, formId, formVersion):
        """Renders form with its schema and uiSchema resolved.
        """
        form = self.get_form(formId, formVersion)['Item']
        form['schema'] = self.client.get_item(TableName='ccmt_cff_schemas', Key=form['schema']['M'])['Item']
        form['schemaModifier'] = self.client.get_item(TableName='ccmt_cff_schemaModifiers', Key=form['schemaModifier']['M'])['Item']
        return form
    def get_form(self, id, version):
        return self.get_item_by_id_and_version('ccmt_cff_forms', id, version)
    def get_schema(self, id, version):
        return self.get_item_by_id_and_version('ccmt_cff_schemas', id, version)
    def get_schemaModifier(self, id, version):
        return self.get_item_by_id_and_version('ccmt_cff_schemaModifiers', id, version)
    def get_item_by_id_and_version(self, tableName, id, version):
        return self.client.get_item(
            TableName=tableName,
            Key={
                'id': {
                    'S': str(id)
                },
                'version': {
                    'N': str(version)
                }
            })
    def update_form(self, id, version, schemaId, schemaModifierId):
        return self.client.update_item(
            TableName='ccmt_cff_forms',
            Key={
                'id': {
                    'S': str(id)
                },
                'version': {
                    'N': str(version)
                }
            },
            UpdateExpression="set schema = :s, schemaModifier =:sm",
            ExpressionAttributeValues={
                ':s': {"M": schemaId},
                ':sm': {"M": schemaModifierId}
            },
            ReturnValues="UPDATED_NEW"

        )
    def submit_form(self, formId, response_data, modifyLink=""):
        formId = ObjectId(formId)
        form = self.db.forms.find_one({"_id": formId}, {"schema": 1, "schemaModifier": 1})
        schemaModifier = self.db.schemaModifiers.find_one({"_id": form['schemaModifier']}, {"paymentInfo": 1, "confirmationEmailInfo": 1})
        result = self.db.responses.insert_one({
            "modifyLink": modifyLink,
            "value": response_data,
            "date_last_modified": datetime.datetime.now(),
            "date_created": datetime.datetime.now(),
            "schema": form['schema'],
            "schemaModifier": form['schemaModifier'],
            "form": formId,
            "paymentInfo": schemaModifier['paymentInfo'],
            "confirmationEmailInfo": schemaModifier['confirmationEmailInfo']
        })
        return {"success": True, "inserted_id": result.inserted_id}
    def render_response_and_schemas(self, responseId):
        """Renders response, plus schema and schemaModifier for that particular response.
        Used for editing responses."""
        response = self.db.responses.find_one({"_id": ObjectId(responseId)})
        schema = self.db.schemas.find_one({"_id": response["schema"]})
        schemaModifier = self.db.schemaModifiers.find_one({"_id": response["schemaModifier"]})
        return [{
            "formData": response,
            "schema": schema,
            "schemaModifier": schemaModifier
        }]
    def edit_response_form(self, responseId, response_data):
        self.db.responses.update_one({
            "_id": responseId
        },
        {
            "$set": {
                "value": response_data,
                "date_last_modified": datetime.datetime.now()
            }
        })