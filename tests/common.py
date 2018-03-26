import unittest
import requests


class CommonTestCase(unittest.TestCase):
    API_KEY = "devdevasdklasjdklajsdlkjd"
    API_ENDPOINT = "https://l5nrf4co1g.execute-api.us-east-1.amazonaws.com/beta/forms"
    FORM_ID = "e4548443-99da-4340-b825-3f09921b4df5"
    FORM_DATA = {"acceptTerms": True, "contact_name": {"last": "test", "first": "test"}, "address": {"zipcode": "test", "state": "test", "city": "test", "line2": "test",
                                                                                                     "line1": "test"}, "email": "aramaswamis@gmail.com", "participants": [{"name": {"last": "test", "first": "test"}, "gender": "M", "race": "5K", "age": 16}]}
    FORM_EXPECTED_RESPONSE = {'paid': False, 'success': True, 'action': 'insert', 'paymentInfo': {'total': 25.0, 'currency': 'USD', 'redirectUrl': 'http://omrun.cmsj.org/training-thankyou/', 'items': [{'name': '2018 CMSJ OM Run',
                                                                                                                                                                                                          'description': 'Registration for Training Only', 'amount': 25.0, 'quantity': 1.0}]}}
    FORM_DATA_TWO = {"acceptTerms": True, "contact_name": {"last": "test", "first": "test"}, "address": {"zipcode": "test", "state": "test", "city": "test", "line2": "test",
                                                                                                         "line1": "test"}, "email": "aramaswamis@gmail.com", "participants": [{"name": {"last": "test", "first": "test"}, "gender": "M", "race": "5K", "age": 16},
                                                                                                                                                                              {"name": {"last": "test2", "first": "test2"}, "gender": "M", "race": "5K", "age": 16}]}
    maxDiff = None

    def api_get(self, action="", params={}, status=200, auth=False):
        """Make a json request to api."""
        return self.api_post(action=action, params=params, status=status, auth=auth, method="GET")

    def api_post(self, action="", params={}, jsondata=None, data=None, status=200, auth=False, method="POST"):
        """Make a json POST request to api."""
        if action:
            params["action"] = action
        if auth:
            params["apiKey"] = self.API_KEY
        if method == "GET":
            r = requests.get(self.API_ENDPOINT, params=params)
        elif method == "POST":
            r = requests.post(self.API_ENDPOINT, params=params,
                              json=jsondata, data=data)
            # if jsondata:
            #     r = requests.post(API_ENDPOINT, params=params, json=jsondata, data=data)
            # else:
            #     r = requests.post(API_ENDPOINT, params=params, data=data)
        try:
            self.assertEqual(r.status_code, status)
        except AssertionError:
            print("===BEGIN DEBUG===")
            print("RES URL", r.url, "\nREQ BODY", r.request.body,
                  "\nREQ HEADERS", r.request.headers, "\nRES JSON", r.json(), "\nJSONDATA", jsondata)
            print("===END DEBUG===")
            raise
        return r.json()

    def submit_with_data(self, data, **kwargs):
        params = {
            "formVersion": 1,
            "formId": self.FORM_ID,
            "modifyLink": "http://cff-test-modify-link"
        }
        body = self.api_post("formSubmit", params=params,
                             jsondata=data, **kwargs)
        return body
        # print(body)
        # responseId = body['res'].pop('id')
        # return body, responseId
