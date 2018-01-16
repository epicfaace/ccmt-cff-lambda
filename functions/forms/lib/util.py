from py_expression_eval import Parser
import flatdict
import re

def deep_access(x, keylist):
    """Access an arbitrary nested part of dictionary x using keylist."""
    val = x
    for key in keylist:
        val = val[key]
    return val

def calculate_price(expressionString, data):
    """Calculates price based on the expression. 
    For example, "participants.age * 12"
    "participants * 12" will use participants' length if it is an array.
    """
    if expressionString[0] == "$": expressionString = expressionString[1:]
    parser = Parser()
    expr = parser.parse(expressionString)
    context = {}
    for variable in expr.variables():
        value = deep_access(data, variable.split("."))
        if type(value) is list:
            value = len(value)
        if not isinstance(value, (int, float)):
            raise ValueError("Key {} is not numeric".format(variable))
        context[variable] = value
    return expr.evaluate(context)

def format_payment(total, currency='USD'):
    if currency == "USD":
        return "${}".format(total)
    return "{} {}".format(currency, total)
def format_paymentInfo(paymentInfo):
    return format_payment(paymentInfo.get("total", "N/A"), paymentInfo.get("currency", "USD"))

def human_readable_key(key, delimiter=":"):
    delimiter = re.escape(delimiter)
    """Makes a delimited key human-readable.
    Ex: participants:0:name --> Participant 1 Name"""
    key = re.sub(r's?{0}(\d+){0}?'.format(delimiter), lambda x: " " + str(int(x.group(1)) + 1) + " ", key)
    key = re.sub(delimiter, ": ", key)
    return key

def dict_to_table(dict, human_readable=True):
    flat = flatdict.FlatDict(dict)
    table = "<table>"
    for key, value in flat.items():
        if human_readable: key = human_readable_key(key)
        table += "<tr><th>{}</th><td>{}</td></tr>".format(key, value)
    table += "</table>"
    return table
