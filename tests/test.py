from .common import CommonTestCase


class TestMain(CommonTestCase):

    def setUp(self):
        pass
    # def test_no_query_string(self):
    #     """Test main endpoint, with no action.
    #     """
    #     body = self.api_get(status=400)
    #     self.assertEqual(body['error'], True)
    #     self.assertIn("No query string provided.", body['message'])

    # def test_api_action_not_found(self):
    #     """Test main endpoint, with no action.
    #     """
    #     body = self.api_get("cff-undefined-action", status=400)
    #     self.assertEqual(body['error'], True)
    #     self.assertIn("Action not found.", body['message'])

    def test_render_form(self):
        """Render form -- see if schema and schemaModifier are defined.
        Todo: actually render the form server-side and use tests to do so.
        """
        data = {
            "version": 1,
            "id": self.FORM_ID,
        }
        body = self.api_get("formRender", data)
        self.assertEqual(body['res']['id'], self.FORM_ID)
        self.assertTrue(body['res']['schema']['value'])
        self.assertTrue(body['res']['schemaModifier']['value'])

    def test_submit_form(self):
        """Submit the form.
        """
        body = self.submit_with_data(self.FORM_DATA)
        responseId = body['res'].pop('id')
        self.assertEqual(body['res'], self.FORM_EXPECTED_RESPONSE)


if __name__ == '__main__':
    unittest.main()
