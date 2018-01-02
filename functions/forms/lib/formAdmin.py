from .mongoConnection import MongoConnection
from bson import ObjectId, json_util

class FormAdmin(MongoConnection):
    def __init__(self, api_key):
        super(FormAdmin, self).__init__()
        center = self.db.centers.find_one({"apiKey": api_key})
        if not center:
            raise Exception("Incorrect API Key. No center found for the specified API key.")
        self.centerId = center["_id"]
        if not self.centerId:
            raise Exception("Center found, but no center ID was existing.")
    def get(self):
        return self.centerId