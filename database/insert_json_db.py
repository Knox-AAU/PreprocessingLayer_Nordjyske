import pymongo  

class DB:

    def __init__(self):
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = myclient["processed_json"]

    def get_json(self, col, params):
        col = self.db[col]
        x = col.find(params)
        return x

    def insert_json(self, col, json):
        col = self.db[col]
        existing_doc = col.find_one(json)
        if not existing_doc:
            x = col.insert_one(json)
        

