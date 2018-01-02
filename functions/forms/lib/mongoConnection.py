from pymongo import MongoClient
import os

mongoClient = MongoClient(os.getenv("CONN_STRING"))
class MongoConnection(object):
    def __init__(self):
        self.db = mongoClient[os.getenv("DB_NAME")]

    #def get_collection(self, name):
    #    self.collection = self.db[name]