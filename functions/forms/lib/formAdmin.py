from .formRender import FormRender
import datetime
from boto3.dynamodb.conditions import Key
from .admin.user import User
import boto3
import uuid
import io

def pickIdVersion(dict):
	# picks the ID and version from a dictionary.
	return {k: dict[k] for k in ["id", "version"]}


"""
"forms::5e258c2c-99da-4340-b825-3f09921b4df5": ["Edit", "Delete", "ViewResponses", "EditResponses", "DeleteResponses"],
"schemaModifiers::0a2e94a9-4ffb-489d-aa34-979fc9df1740": ["Edit", "Delete"],
"forms::e4548443-99da-4340-b825-3f09921b4df5": ["Edit", "Delete"],
"schemaModifiers::0a2e94a9-4ffb-489d-aa34-cdd4660d9d30": ["Edit", "Delete"],
"schemas::5e258c2c-9b85-40ad-b764-979fc9df1740": ["Edit", "Delete"]
"""
"""class FormAdmin(FormRender):
	def __init__(self, alias, apiKey):
		super(FormAdmin, self).__init__(alias)
		user_permission = self.user_permissions.get_item(Key={"id": apiKey})[
														 "Item"]
		if not user_permission:
		   raise Exception(
			   "No user permission entry found for the specified user id; please request one for user id: " + apiKey)
		self.user = User(user_permission)
	def list_forms(self):
		keys = self.user.get_form_list_keys()
		# raise Exception(keys)
		response = self.dynamodb.batch_get_item(
		RequestItems={
			self.forms.table_name: {
				'Keys': keys,
				'ConsistentRead': True
			}
		})
		return response["Responses"][self.forms.table_name]
	def get_form_responses(self, formId, formVersion):
		if not self.user.can_view_responses(formId):
			return False
"""


class FormAdmin(FormRender):
	def __init__(self, alias, apiKey):
		super(FormAdmin, self).__init__(alias)
		center = self.centers.get_item(Key={"apiKey": apiKey})["Item"]
		if not center:
		   raise Exception("Incorrect API Key. No center found for the specified API key.")
		self.centerId = center["id"]
		if not self.centerId:
		   raise Exception("Center found, but no center ID found.")
		self.apiKey = apiKey
	def list_forms(self):
		forms = self.forms.query(
			IndexName='center-index',
			#KeyConditionExpression=Key('center').eq(self.centerId)
			KeyConditionExpression='center = :c',
			ExpressionAttributeValues={ ':c': self.centerId} 
		)
		return forms["Items"]
	def get_form_responses(self, formId, formVersion, format, filter):
		form = self.forms.get_item(Key={"id": formId, "version": int(formVersion)})["Item"]
		if (form["center"] != self.centerId):
			raise Exception("Your center does not have access to this form.")
		responses = self.responses.query(
			KeyConditionExpression=Key('formId').eq(formId)
		)["Items"]
		return responses
	"""def agg_form_responses(self, formId, formVersion):
		form = self.forms.get_item(Key={"id": formId, "version": int(formVersion)}, ProjectionExpression="schemaModifier")["Item"]
		# todo: add a check here for security.
		dataOptions = self.schemaModifiers.get_item(Key=form["schemaModifier"], ProjectionExpression="dataOptions")["Item"]

		if filter == "PAID":
			return [res for res in responses if res.get("PAID", None)]
		if format == "xlsx":
			output = io.BytesIO()
			df = pd.DataFrame(responses)
			writer = pd.ExcelWriter(output, engine='xlsxwriter')
			df.to_excel(writer, sheet_name='Responses')
			writer.save()
			xlsx_data = output.getvalue()
			return {"returnType": "xlsx", "body": xlsx_data}
		else:
		return aggregate"""
	"""def export_responses(self, formId, formVersion):
		responses = self.get_form_responses(formId, formVersion)"""
	def update_form_entry(self, formId, formVersion, body):
		# Helper function.
		formKey = {"id": formId, "version": int(formVersion)}
		form = self.forms.get_item(Key=formKey)["Item"]
		formUpdateExpression = []
		formExpressionAttributeValues = {}
		formExpressionAttributeNames = {}
		if "schema" in body and body["schema"]["version"] != form["schema"]["version"]:
			# schema is a reserved keyword
			formUpdateExpression.append("#schema = :s")
			formExpressionAttributeNames["#schema"] = "schema"
			formExpressionAttributeValues[":s"] = pickIdVersion(body["schema"])
		if "schemaModifier" in body and body["schemaModifier"] != form["schemaModifier"]:
			formUpdateExpression.append("schemaModifier = :sm")
			formExpressionAttributeValues[":sm"] = pickIdVersion(body["schemaModifier"])
		if "couponCodes" in body:
			formUpdateExpression.append("couponCodes = :cc")
			formExpressionAttributeValues[":cc"] = body["couponCodes"]
		if "name" in body:
			# name is a reserved keyword so need to do it this way:
			formUpdateExpression.append("#name = :n")
			formExpressionAttributeNames["#name"] = "name"
			formExpressionAttributeValues[":n"] = body["name"]
		formUpdateExpression.append("date_last_modified = :now")
		formExpressionAttributeValues[":now"] = datetime.datetime.now().isoformat()
		if len(formUpdateExpression) == 0:
			raise Exception("Nothing to update.")
		return self.forms.update_item(
			Key=formKey,
			UpdateExpression= "SET " + ",".join(formUpdateExpression),
			ExpressionAttributeValues=formExpressionAttributeValues,
			ExpressionAttributeNames=formExpressionAttributeNames,
			ReturnValues="UPDATED_NEW"
		)["Attributes"]
	def upsert_s_or_sm_entry(self, collection, data):
		# Helper function. Puts (replaces) item; increments version # if # is "NEW".
		if data["version"] == "NEW":
			data["version"] = self.get_latest_version(collection, data["id"]) + 1
			data["date_created"] = datetime.datetime.now().isoformat()
		data["date_last_modified"] = datetime.datetime.now().isoformat()
		collection.put_item(
			Item=data
		)
		return data
	def edit_form(self, formId, formVersion, body):
		"""if "schema" in body:
			body["schema"] = self.upsert_s_or_sm_entry(self.schemas, body["schema"])
		"""
		if "schemaModifier" in body:
			body["schemaModifier"] = self.upsert_s_or_sm_entry(self.schemaModifiers, body["schemaModifier"])
		body["form"] = self.update_form_entry(formId, formVersion, body)
		body['schema_versions'] = self.get_versions(self.schemas, body['schema']['id'])
		body['schemaModifier_versions'] = self.get_versions(self.schemaModifiers, body['schemaModifier']['id'])
		return {
			"success": True,
			"updated_values": body
		}
	"""def duplicate_form(self, formId, formVersion):
		form = self.render_form_by_id()
		schema = self.get_schema(form)
	def create_form(self, schemaId=None, schemaVersion=None):
		if not (schemaId and schemaVersion):
			schema = self.upsert_s_or_sm_entry(self.schemas, {"id": uuid.uuid4(), "version": 1})
		schemaModifier = self.upsert_s_or_sm_entry(self.schemaModifiers, {"id": uuid.uuid4(), "version": 1})
		form = {
				"id": uuid.uuid4(),
				"center": self.centerId,
				"version": 1,
				"schema": {
					"id": schema['id'],
					"version": schema['version'],
				},
				"schemaModifier": {
					"id": schemaModifier['id'],
					"version": schemaModifier['version']
				}
			}
		self.forms.put_item(
			Item=form
		)
		return form"""