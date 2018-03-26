from .common import CommonTestCase
class TestCouponCodes(CommonTestCase):
    ERR_COUPON_CODES_MAX_REACHED = "Coupon code maximum reached.\nSubmitting this form will cause you to exceed the coupon code maximum.\nNumber of spots remaining: {}"
    def test_submit_not_found_coupon_code(self):
        """Submit form with coupon code not found.
        Todo: fix this in the client / server side! It should return a 400 instead.
        """
        couponCode = "cff-unittest-coupon-code-not-found"
        data = dict(self.FORM_DATA, **{"couponCode": couponCode})
        body = self.submit_with_data(data, status=200)
        self.assertEqual(body['res'], {
                         'success': False, 'message': 'Coupon Code not found.', 'fields_to_clear': ['couponCode']})

    def test_submit_coupon_code_max(self):
        """Submit form with an already maxed out coupon code.
        """
        couponCodes = ["cff-unittest-coupon-code-maxed-out", "cff-unittest-coupon-code-countBy-maxed-out-at-30"]
        for couponCode in couponCodes:
            with self.subTest(couponCode=couponCode):
                data = dict(self.FORM_DATA, **{"couponCode": couponCode})
                body = self.submit_with_data(data, status=200)
                self.assertEqual(body['res'], {
                                'success': False, 'message': self.ERR_COUPON_CODES_MAX_REACHED.format(0), 'fields_to_clear': ['couponCode']})
    def test_submit_coupon_code_max_one_remaining(self):
        """When a coupon code only has remaining, it should not accept a response with 2 participants (as it would overshoot the max).
        """
        couponCode = "cff-unittest-coupon-code-countBy-max-30-one-remaining"
        data = dict(self.FORM_DATA_TWO, **{"couponCode": couponCode})
        body = self.submit_with_data(data, status=200)
        self.assertEqual(body['res'], {
                        'success': False, 'message': self.ERR_COUPON_CODES_MAX_REACHED.format(1), 'fields_to_clear': ['couponCode']})

    def test_submit_coupon_code_responses(self):
        """Submit form with a coupon code based on responses.
        """
        couponCode = "cff-unittest-coupon-code-countBy-responses"
        data = dict(self.FORM_DATA, **{"couponCode": couponCode})
        body = self.submit_with_data(data, status=200)
        responseId = body['res'].pop("id")
        expected_response = {'action': 'insert',
                             'paid': True,
                             'paymentInfo': {'currency': 'USD',
                                             'items': [{'amount': 25.0,
                                                        'description': 'Registration for Training Only',
                                                        'name': '2018 CMSJ OM Run',
                                                        'quantity': 1.0},
                                                       {'amount': -25.0,
                                                        'description': 'Coupon Code',
                                                        'name': 'Coupon Code',
                                                        'quantity': 1.0}],
                                             'redirectUrl': 'http://omrun.cmsj.org/training-thankyou/',
                                             'total': 0.0},
                             'success': True}
        self.assertEqual(body['res'], expected_response)

    def test_submit_coupon_code_participants(self):
        """Submit form with a coupon code based on participants.
        """
        couponCode = "cff-unittest-coupon-code-countBy-participants"
        data = dict(self.FORM_DATA, **{"couponCode": couponCode})
        body = self.submit_with_data(data, status=200)
        responseId = body['res'].pop("id")
        expected_response = {'action': 'insert',
                             'paid': False,
                             'paymentInfo': {'currency': 'USD',
                                             'items': [{'amount': 25.0,
                                                        'description': 'Registration for Training Only',
                                                        'name': '2018 CMSJ OM Run',
                                                        'quantity': 1.0},
                                                       {'amount': -5.0,
                                                        'description': 'Coupon Code',
                                                        'name': 'Coupon Code',
                                                        'quantity': 1.0}],
                                             'redirectUrl': 'http://omrun.cmsj.org/training-thankyou/',
                                             'total': 20.0},
                             'success': True}
        self.assertEqual(body['res'], expected_response)
    
    def test_create_coupon_code_and_submit_max(self):
        """Create coupon code and submit max.
        """
        pass