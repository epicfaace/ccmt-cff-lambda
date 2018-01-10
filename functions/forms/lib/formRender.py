from .mongoConnection import MongoConnection
from bson import ObjectId
import datetime

class FormRender(MongoConnection):
    def render_form_by_id(self, formId):
        """Renders form with its schema and uiSchema resolved.
        """
        return self.db.forms.aggregate([
        {"$match": {"_id": ObjectId(formId)} },
        {"$lookup":
            {
                "from": "schemas",
                "localField": "schema",
                "foreignField": "_id",
                "as": "schemaRef"
            }
        },
        {"$lookup":
            {
                "from": "schemaModifiers",
                "localField": "schemaModifier",
                "foreignField": "_id",
                "as": "schemaModifierRef"
            }
        },
        { "$project": { 
                "name": 1,
                "schema": { "$arrayElemAt": [ "$schemaRef", 0 ] },
                "schemaModifier": { "$arrayElemAt": [ "$schemaModifierRef", 0 ] } 
            }} 
        ])
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
                "value": response_data
            }
        })