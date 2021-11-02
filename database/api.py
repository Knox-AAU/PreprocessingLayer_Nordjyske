from flask import Flask, jsonify, request, abort
from flask.wrappers import Response
from insert_json_db import DB
from bson.json_util import dumps
import json 
from knox_source_data_io.io_handler import IOHandler

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World!'

@app.route("/get_json", methods=["GET"])
def get_json():
    col = request.args.get("col", default = None, type = str)
    field = request.args.get('field', default = None, type = str)
    val = request.args.get('val', default = None, type = str)
    if col is None or field is None or val is None:
        return abort(Response("missing col, field or val arg"))
    list_res = list(DB().get_json(col, {field: val}))
    return dumps(list_res)

@app.route("/insert_json", methods=["POST"])
def post_json():
    j_str = request.get_json()
    if j_str is None:
        return abort(Response("missing json"))
    try:
        IOHandler.validate_json()
    except Exception as e:
        abort(Response("fucky"))
    return Response(status=200)
    
    

app.run()