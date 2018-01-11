from .dbConnection import DBConnection
import datetime
import uuid
# Ref:
# https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GettingStarted.Python.03.html

class FormRender(DBConnection):
    def render_form_by_id(self, formId, formVersion):
        """Renders form with its schema and uiSchema resolved.
        """
        form = self.get_form(formId, formVersion)
        self.set_form_schemas(form)
        return form
    def set_form_schemas(self, form):
        """Renders form with its schema and uiSchema resolved.
        """
        form['schema'] = self.schemas.get_item(Key=form['schema'])["Item"]
        form['schemaModifier'] = self.schemaModifiers.get_item(Key=form['schemaModifier'])["Item"]
        return form
    def get_form(self, id, version):
        return self.forms.get_item(Key={"id": id, "version": version})["Item"]
    def get_schema(self, id, version):
        return self.schemas.get_item(Key={"id": id, "version": version})["Item"]
    def get_schemaModifier(self, id, version):
        return self.schemaModifiers.get_item(Key={"id": id, "version": version})["Item"]
    def update_form(self, id, version, schemaId, schemaModifierId):
        # Not used.
        return self.forms.update_item(
            Key={
                'id': str(id),
                'version': str(version)
            },
            UpdateExpression="set schema = :s, schemaModifier =:sm",
            ExpressionAttributeValues={
                ':s': schemaId,
                ':sm': schemaModifierId
            },
            ReturnValues="UPDATED_NEW"
        )
    def submit_form(self, formId, formVersion, response_data, modifyLink=""):
        form = self.get_form(formId, formVersion)
        schemaModifier = self.schemaModifiers.get_item(Key=form['schemaModifier'])['Item']
        resId = str(uuid.uuid4())
        self.responses.put_item(
            Item={
            "formId": formId, # partition key
            "responseId": resId, # sort key
            "modifyLink": modifyLink,
            "value": response_data,
            "date_last_modified": datetime.datetime.now().isoformat(),
            "date_created": datetime.datetime.now().isoformat(),
            "form": {
                    'id': formId,
                    'version': formVersion
            }, # id, version.
            "paymentInfo": schemaModifier['paymentInfo'],
            "confirmationEmailInfo": schemaModifier['confirmationEmailInfo']
        })
        return {"success": True, "inserted_id": resId }
    def render_response_and_schemas(self, formId, responseId):
        """Renders response, plus schema and schemaModifier for that particular response.
        Used for editing responses."""
        response = self.responses.get_item(Key={"formId": formId, "responseId": responseId})["Item"]
        form = self.forms.get_item(Key={"id": formId})["Item"]
        self.set_form_schemas(form)
        return [{
            "formData": response,
            "schema": form['schema'],
            "schemaModifier": form['schemaModifier']
        }]
    def edit_response_form(self, formId, formVersion, responseId, response_data):
        """self.db.responses.update_one({
            "_id": responseId
        },
        {
            "$set": {
                "value": response_data,
                "date_last_modified": datetime.datetime.now()
            }
        })"""
        pass