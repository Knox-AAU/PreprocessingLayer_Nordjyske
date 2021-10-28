from flask import Flask, jsonify, request, abort
from flask.wrappers import Response
from insert_json_db import DB
from bson.json_util import dumps

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
def get_json():
    col = request.args.get("col", default = None, type = str)
    field = request.args.get('field', default = None, type = str)
    val = request.args.get('val', default = None, type = str)
    if col is None or field is None or val is None:
        return abort(Response("missing col, field or val arg"))
    list_res = list(DB().get_json(col, {field: val}))
    return dumps(list_res)

app.run()