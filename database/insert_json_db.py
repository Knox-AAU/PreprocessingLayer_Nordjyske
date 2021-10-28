from os import stat
import pymongo  
import json

class DB:

    def __init__(self):
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = myclient["processed_json"]
        
    def test():

        with open("/home/aau/Desktop/newoutput/2017-06-10_aalborg.json") as j:
            file = json.load(j)
            #x = nordCol.insert_one(file)

        # if "Nordjyske" in collist:
        #   print("The collection exists.")
        #print(x.inserted_id)
        #print(myclient.list_database_names())

    def get_json(self, col_name, params):
        col = self.db[col_name]
        x = col.find(params)
        return x

    def insert_json(self, col, json):
        col = self.db[col]
        x = col.find(params)
        return x
