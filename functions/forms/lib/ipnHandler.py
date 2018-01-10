import sys
import urllib.parse
import requests
import datetime
from bson import ObjectId
from .mongoConnection import MongoConnection
from .emailer import Emailer
import json
from json2html import json2html

"""
action=ipn&cmd=_notify-validate&mc_gross=19.95&protection_eligibility=Eligible&address_status=confirmed&payer_id=LPLWNMTBWMFAY&tax=0.00&address_street=1+Main+St&payment_date=20%3A12%3A59+Jan+13%2C+2009+PST&payment_status=Completed&charset=windows-1252&address_zip=95131&first_name=Test&mc_fee=0.88&address_country_code=US&address_name=Test+User&notify_version=2.6&custom=&payer_status=verified&address_country=United+States&address_city=San+Jose&quantity=1&verify_sign=AtkOfCXbDm2hu0ZELryHFjY-Vb7PAUvS6nMXgysbElEn9v-1XcmSoGtf&payer_email=gpmac_1231902590_per%40paypal.com&txn_id=61E67681CH3238416&payment_type=instant&last_name=User&address_state=CA&receiver_email=gpmac_1231902686_biz%40paypal.com&payment_fee=0.88&receiver_id=S8XGHLYDW9T3S&txn_type=express_checkout&item_name=&mc_currency=USD&item_number=&residence_country=US&test_ipn=1&handling_amount=0.00&transaction_subject=&payment_gross=19.95&shipping=0.00

Full list of IPN variables: https://developer.paypal.com/docs/classic/ipn/integration-guide/IPNandPDTVariables/

{
        "mc_gross": "25.00",
        "protection_eligibility": "Eligible",
        "address_status": "confirmed",
        "payer_id": "A4CSL993V3BDG",
        "address_street": "1 Main St",
        "payment_date": "11:27:19 Jan 07, 2018 PST",
        "payment_status": "Completed",
        "charset": "windows-1252",
        "address_zip": "95131",
        "first_name": "test",
        "mc_fee": "1.03",
        "address_country_code": "US",
        "address_name": "test buyer",
        "notify_version": "3.8",
        "custom": "5a527474bdc24800015b8034",
        "payer_status": "verified",
        "business": "aramaswamis-facilitator@gmail.com",
        "address_country": "United States",
        "address_city": "San Jose",
        "quantity": "1",
        "verify_sign": "AnJ2HUJsm40z244.ABNEwFR12hcFAGNgnedQIC2BPo3UV35k2cCQrzGk",
        "payer_email": "aramaswamis-buyer@gmail.com",
        "txn_id": "3H3308841Y0633836",
        "payment_type": "instant",
        "last_name": "buyer",
        "address_state": "CA",
        "receiver_email": "aramaswamis-facilitator@gmail.com",
        "payment_fee": "1.03",
        "receiver_id": "T4A6C58SP7PP2",
        "txn_type": "express_checkout",
        "mc_currency": "USD",
        "residence_country": "US",
        "test_ipn": "1",
        "payment_gross": "25.00",
        "ipn_track_id": "562abbbb392ab",
        "cmd": "_notify-validate"
    }
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
        paramDict = dict(params)
        responseId = ObjectId(paramDict["custom"])
        if r.text == 'VERIFIED':
            # payment_status completed.
            mongoConnection.db.responses.update_one({
                "_id": responseId
                },
                {
                    "$inc": {
                        "IPN_TOTAL_AMOUNT": float(paramDict["mc_gross"])
                    },
                    "$push": {
                        "IPN_HISTORY": {
                            "date": datetime.datetime.now(),
                            "value": paramDict
                        }
                    },
                    "$set": {
                        "IPN_STATUS": paramDict["payment_status"],
                        "PAID": paramDict["payment_status"] == "Completed"
                    }
                }
            )
            response = mongoConnection.db.responses.find_one({
                "_id": responseId
            }, {"value": 1, "confirmationEmailInfo": 1, "paymentInfo": 1, "modifyLink": 1})
            if "confirmationEmailInfo" in response and response["confirmationEmailInfo"]:
                toField = response["confirmationEmailInfo"]["toField"]
                msgBody = response["confirmationEmailInfo"].get("message", "")
                if response["confirmationEmailInfo"]["showResponse"]:
                    msgBody += "<br><br>" + json2html.convert(response["value"], clubbing=False, table_attributes="'border'=0")
                if response["confirmationEmailInfo"]["showModifyLink"] and "modifyLink" in response:
                    msgBody += "<br><br>Modify your response by going to this link: {}".format(response["modifyLink"] + "#resid=" + str(responseId))
                # todo: check amounts and Completed status, and then send.
                emailer = Emailer()
                emailer.send_email(toEmail=response["value"][toField],
                                    fromEmail=response["confirmationEmailInfo"].get("from", "webmaster@chinmayamission.com"),
                                    fromName=response["confirmationEmailInfo"].get("fromName", "Webmaster"),
                                    subject=response["confirmationEmailInfo"].get("subject", "Confirmation Email"),
                                    msgBody=msgBody)
            return params
        elif r.text == 'INVALID':
            mongoConnection.db.ipn.insert_one({
                "date_created": datetime.datetime.now(),
                "success": False,
                "params": params,
                "IPN_RESPONSE": "INVALID"
            })
            return "invalid"
        else:
            return "else"