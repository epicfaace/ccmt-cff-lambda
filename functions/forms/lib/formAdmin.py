from .mongoConnection import MongoConnection
from bson import ObjectId, json_util

class FormAdmin(MongoConnection):
    def __init__(self, apiKey):
        super(FormAdmin, self).__init__()
        center = self.db.centers.find_one({"apiKey": apiKey})
        if not center:
           raise Exception("Incorrect API Key. No center found for the specified API key.")
        self.centerId = center["_id"]
        if not self.centerId:
           raise Exception("Center found, but no center ID found.")
        self.apiKey = apiKey
    def list_forms(self):
        return self.db.forms.find({ "center": self.centerId }, {"name": 1, "_id": 1})
    def performFormAgg(self, aggPipeline=[]):
        """Performs aggregation only on forms which user has access to.
        """
        pipeline = [
            {"$match": {"center": self.centerId, "_id": self.formId } }
        ] + aggPipeline
        return self.db.forms.aggregate(pipeline)
    def get_form_responses(self, formId):
        self.formId = ObjectId(formId)
        return self.performFormAgg([
        {"$lookup":
            {
                "from": "responses",
                "localField": "_id",
                "foreignField": "form",
                "as": "responses"
            }
        }
        ])