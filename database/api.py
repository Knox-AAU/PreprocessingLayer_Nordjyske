from flask import Flask, jsonify, request, abort
from flask.wrappers import Response
from mongoDB import DB
from bson.json_util import dumps
import json 
from bson.objectid import ObjectId
from knox_source_data_io.io_handler import IOHandler
import traceback

app = Flask(__name__)
db = DB()

@app.route('/')
def hello():
    return 'Hello, World!'

@app.route("/get_json", methods=["GET"])
def get_json():
    col = request.args.get("col", default = None, type = str)
    field = request.args.get('field', default = None, type = str)
    val = request.args.get('val', default = None, type = str)
    if col is None or field is None or val is None:
        return abort(Response(reponse="request url must include: col, field or val args"), status=400)
    res = list(db.get_json(col, {field: val}))
    for o in res:
        o["_id"] = str(o["_id"])
    return Response(response=dumps(res), status=200, mimetype="application/json")

@app.route("/insert_json", methods=["POST"])
def post_json():
    j_str = request.get_json()
    if j_str is None:
        return abort(Response("missing json"))
    try:
        IOHandler.validate_json(j_str, "../publication.schema.json")
    except Exception as e:
        traceback.print_exc(e)
        return abort(Response("bad json"))
    col = request.args.get("col", default = None, type = str)
    res = (str)(DB().insert_json(col, j_str))
    print(res)
    return Response(response=json.dumps({"message": "json inserted", "id": res}), status=200, mimetype="application/json")
        
        
if __name__ == "__main__":
    app.run(port=5000, debug=True)