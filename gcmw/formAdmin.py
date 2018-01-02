from .mongoConnection import MongoConnection
from bson import ObjectId

class FormAdmin(MongoConnection):
    def render_form_by_id(formId, version=0):
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