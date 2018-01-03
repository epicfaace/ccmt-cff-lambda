import sys
import urllib.parse
import requests
import datetime
from .mongoConnection import MongoConnection

"""
action=ipn&cmd=_notify-validate&mc_gross=19.95&protection_eligibility=Eligible&address_status=confirmed&payer_id=LPLWNMTBWMFAY&tax=0.00&address_street=1+Main+St&payment_date=20%3A12%3A59+Jan+13%2C+2009+PST&payment_status=Completed&charset=windows-1252&address_zip=95131&first_name=Test&mc_fee=0.88&address_country_code=US&address_name=Test+User&notify_version=2.6&custom=&payer_status=verified&address_country=United+States&address_city=San+Jose&quantity=1&verify_sign=AtkOfCXbDm2hu0ZELryHFjY-Vb7PAUvS6nMXgysbElEn9v-1XcmSoGtf&payer_email=gpmac_1231902590_per%40paypal.com&txn_id=61E67681CH3238416&payment_type=instant&last_name=User&address_state=CA&receiver_email=gpmac_1231902686_biz%40paypal.com&payment_fee=0.88&receiver_id=S8XGHLYDW9T3S&txn_type=express_checkout&item_name=&mc_currency=USD&item_number=&residence_country=US&test_ipn=1&handling_amount=0.00&transaction_subject=&payment_gross=19.95&shipping=0.00


"""

class IpnHandler:
    def ipnHandler(self, param_str):
        sandbox = True
        VERIFY_URL_PROD = 'https://www.paypal.com/cgi-bin/webscr'
        VERIFY_URL_TEST = 'https://www.sandbox.paypal.com/cgi-bin/webscr'

        # Switch as appropriate
        VERIFY_URL = VERIFY_URL_TEST if sandbox else VERIFY_URL_PROD

        # Read and parse query string
        # param_str = sys.stdin.readline().strip()
        
        params = urllib.parse.parse_qsl(param_str)
        
        # Add '_notify-validate' parameter
        params.append(('cmd', '_notify-validate'))

        # Post back to PayPal for validation
        headers = {'content-type': 'application/x-www-form-urlencoded', 'host': 'www.paypal.com'}
        r = requests.post(VERIFY_URL, params=params, headers=headers, verify=True)
        r.raise_for_status()

        # Check return message and take action as needed
        mongoConnection = MongoConnection()
        if r.text == 'VERIFIED':
            # payment_status  completed. 
            mongoConnection.db.ipn.insert_one({
                "date_created": datetime.datetime.now(),
                "data": params
            })
            return params
        elif r.text == 'INVALID':
            mongoConnection.db.ipn.insert_one({
                "date_created": datetime.datetime.now(),
                "data": "invalid",
                "params": params
            })
            return "invalid"
        else:
            return "else"