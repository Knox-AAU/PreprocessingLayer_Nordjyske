import pymongo  

class DB:

    def __init__(self):
        try:
            myclient = pymongo.MongoClient("mongodb://localhost:27017/")
            myclient.server_info() # trigger exception if cannot connect to db
            self.db = myclient["processed_json"]
        except:
            print("Could not connect to database")

    def get_json(self, col, params):
        col = self.db[col]
        res = list(col.find(params))
        for o in res:
            o["_id"] = str(o["_id"])
        return res
    
    def get_all_from_col(self, col):
        res = list(self.db[col].find({}))
        for o in res:
            o["_id"] = str(o["_id"])
        return res

    def insert_json(self, col, json):
        col = self.db[col]
        existing_doc = col.find_one(json)
        if not existing_doc:
            x = col.insert_one(json)
            return (str)(x.inserted_id )
        return None

