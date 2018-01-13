from py_expression_eval import Parser

def deep_access(x, keylist):
    """Access an arbitrary nested part of dictionary x using keylist."""
    val = x
    for key in keylist:
        val = val[key]
    return val

def calculate_price(expressionString, data):
    """Calculates price based on the expression. 
    For example, "participants.age * 12"
    "participants * 12" will use participants' length if it is an array.abs
    """
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