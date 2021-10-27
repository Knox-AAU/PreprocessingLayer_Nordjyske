import pymongo  
import json


myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["processed_json"]

nordCol = mydb["Nordjyske"]

with open("/home/aau/Desktop/newoutput/2017-06-10_aalborg.json") as j:
    file = json.load(j)
    #x = nordCol.insert_one(file)

collist = mydb.list_collection_names()
# if "Nordjyske" in collist:
#   print("The collection exists.")
#print(x.inserted_id)
#print(myclient.list_database_names())
x = nordCol.find({"generator.generated_at": "2021-10-26T09:48:07.458238"})

for i in x:
    print(i)