from chalicelib.models import Form, Response, serialize_model
import bson
from bson.objectid import ObjectId
from pydash.objects import get
from bson.json_util import dumps
import json

def form_response_list(formId):
    """Show all responses for a particular form.
    Example
    /responses?query=test
    /responses?query=test&autocomplete=1
    /responses?query=5cdf&autocomplete=1&search_by_id=1
    """
    from ..main import app
    form = Form.objects.only("formOptions", "cff_permissions").get({"_id":ObjectId(formId)})
    # todo: use search framework, don't return all!
    query = app.current_request.query_params and app.current_request.query_params.get("query", None)
    autocomplete = app.current_request.query_params and app.current_request.query_params.get("autocomplete", None)
    search_by_id = app.current_request.query_params and app.current_request.query_params.get("search_by_id", None)
    show_unpaid = app.current_request.query_params and app.current_request.query_params.get("show_unpaid", None)
    if query:
        # autocomplete, participant name, assign bibs functionality
        app.check_permissions(form, ["Responses_View", "Responses_CheckIn"])
        search_fields = get(form.formOptions.dataOptions, "search.searchFields", ["_id"])
        if search_by_id is not None:
            search_fields = ["_id"]
        result_limit = get(form.formOptions.dataOptions, "search.resultLimit", 10)
        result_fields = get(form.formOptions.dataOptions, "search.resultFields", ["_id"])
        autocomplete_fields = get(form.formOptions.dataOptions, "search.autocompleteFields", ["_id"])
        if show_unpaid is not None:
            default_mongo_query = {"paid": False}
        else:
            default_mongo_query = {"paid": True}
        mongo_query = {"$or": []}
        for word in query.split(" "):
            for field in search_fields:
                if field == "_id":
                    if len(word) <= 24:
                        try:
                            queryObjectIdStart = ObjectId(word + "0" * (24 - len(word))) # fill in zeroes to create object id, e.g. 5cba --> 5cba0000000000000000000
                            queryObjectIdEnd = ObjectId(word + "e" * (24 - len(word)))
                            mongo_query["$or"].append({field: {"$gte": queryObjectIdStart, "$lte": queryObjectIdEnd} })
                        except bson.errors.InvalidId:
                            pass
                else:
                    if field.startswith("value.participants."):
                        _, subfield = field.split("value.participants.")
                        mongo_query["$or"].append({"value.participants": {
                                "$elemMatch": {
                                    subfield: {
                                        "$regex": '^' + word, "$options" : "i"
                                    }
                                }
                            }
                        })
                    else:
                        mongo_query["$or"].append({field: {"$regex": '^' + word, "$options" : "i"}})
        mongo_query["form"] = form.id
        if len(mongo_query["$or"]) == 0:
            del mongo_query["$or"]
        # Default query paid = True
        if mongo_query:
            mongo_query = {"$and": [default_mongo_query, mongo_query]}
        else:
            mongo_query = default_mongo_query
        if autocomplete is not None:
            projection = {field: 1 for field in autocomplete_fields}
            result_limit = 5
        else:
            projection = {}
            for field in result_fields:
                projection[field] = 1
        responses = Response.objects.raw(mongo_query).limit(result_limit).project(projection)
    else:
        app.check_permissions(form, ["Responses_View"])
        responses = Response.objects.all()._collection.find({"form": form.id}, {"value": 1, "_id": 1, "amount_paid": 1, "user": 1, "form": 1, "paymentInfo": 1, "date_created": 1, "date_modified": 1, "paid": 1, "counter": 1})
        return {"res": [r for r in json.loads(dumps(responses))] }
    return {"res": [serialize_model(r) for r in responses]}