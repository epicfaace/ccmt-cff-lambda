def coupon_code_verify_max(form, code, responseId=None):
    # True: coupon code can be used (either length of coupon codes used is not at max, or your ID has already used the coupon code before.)
    responses = form.get("couponCodes_used", {}).get(code, {}).get("responses", [])
    maximum = form.get("couponCodes", {}).get(code, {}).get("max", 0)
    return responseId in responses or len(responses) < maximum

def coupon_code_record_as_used(formsCollection, form, code, responseId):
    # form = formsCollection.get_item(Key=formKey)["Item"]
    # code = "TEST"
    # responseId = "123123-123123"
    formKey = {"id": form['id'], "version": int(form['version'])}
    path = "couponCodes_used.{}.responses".format(code)
    if "couponCodes_used" in form:
        if code in form["couponCodes_used"] and "responses" in form["couponCodes_used"][code]:
            if responseId in form["couponCodes_used"][code]["responses"]:
                return True
            else:
                path = "couponCodes_used.{}.responses".format(code)
                formsCollection.update_item(
                    Key = formKey,
                    UpdateExpression="SET {0} = list_append(if_not_exists({0}, :empty_list), :responseId)".format(path),
                    ExpressionAttributeValues = {
                        ":responseId": [responseId],
                        ":empty_list": []
                    },
                    ConditionExpression="attribute_exists({})".format(path)
                )
        else:
            path = "couponCodes_used.{}".format(code)
            formsCollection.update_item(
                Key = formKey,
                UpdateExpression="SET {0} = :couponCodeValue".format(path),
                ExpressionAttributeValues = {
                    ":couponCodeValue": {"responses": [responseId] }
                }
            )
    else:
        formsCollection.update_item(
            Key = formKey,
            UpdateExpression="SET couponCodes_used = :couponCodes_used",
            ExpressionAttributeValues = {
                ":couponCodes_used": {code: {"responses": [responseId] } }
            }
        )
    return True