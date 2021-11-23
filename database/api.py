from flask import Flask, request, abort
from flask.wrappers import Response
from mongoDB import DB
from bson.json_util import dumps
import json
from knox_source_data_io.io_handler import IOHandler
import traceback

app = Flask(__name__)
db = DB()


@app.route("/get_json", methods=["GET"])
def get_json():
    col = request.args.get("col", default=None, type=str)
    field = request.args.get("field", default=None, type=str)
    val = request.args.get("val", default=None, type=str)
    check_missing_args("col, field and val", col, field, val)
    res = db.get_json(col, {field: {"$regex": val}})
    return Response(response=dumps(res), status=200, mimetype="application/json")


@app.route("/get_all_json", methods=["GET"])
def get_all_json():
    col = request.args.get("col", default=None, type=str)
    check_missing_args(col, "col")
    res = db.get_all_from_col(col)
    return Response(response=dumps(res), status=200, mimetype="application/json")


@app.route("/insert_json", methods=["POST"])
def post_json():
    col = request.args.get("col", default=None, type=str)
    j_str = request.get_json()
    check_missing_args(col, "col")
    if j_str is None:
        return abort(Response("missing json"), status=400)
    try:
        IOHandler.validate_json(j_str, "../publication.schema.json")
    except Exception as e:
        traceback.print_exc(e)
        return abort(Response("Json could not be validated"), status=400)
    res = DB().insert_json(col, j_str)
    if res is None:
        return Response(
            response=json.dumps(
                {
                    "message": "Json is duplicate and has already been inserted",
                    "id": "None",
                }
            ),
            status=200,
            mimetype="application/json",
        )
    else:
        return Response(
            response=json.dumps({"message": "json inserted", "id": res}),
            status=200,
            mimetype="application/json",
        )


def check_missing_args(must_include, *args):
    for arg in args:
        if arg is None or arg == "":
            return abort(
                Response(
                    response=f"Bad request. url must include: {must_include}", status=400
                )
            )

if __name__ == "__main__":
    app.run(port=5000, debug=True)
