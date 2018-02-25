def coupon_code_verify_max(form, code, responseId=None):
    # True: coupon code can be used (either length of coupon codes used is not at max, or your ID has already used the coupon code before.)
    # If maximum is negative, that means there is no maximum.
    responses = form.get("couponCodes_used", {}).get(code, {}).get("responses", [])
    maximum = form.get("couponCodes", {}).get(code, {}).get("max", -1)
    return responseId in responses or maximum < 0 or len(responses) < maximum

def coupon_code_record_as_used(formsCollection, form, code, responseId):
    # form = formsCollection.get_item(Key=formKey)["Item"]
    # code = "TEST"
    # responseId = "123123-123123"
    formKey = {"id": form['id'], "version": int(form['version'])}
    if "couponCodes_used" in form:
        if code in form["couponCodes_used"] and "responses" in form["couponCodes_used"][code]:
            if responseId in form["couponCodes_used"][code]["responses"]:
                return True
            else:
                formsCollection.update_item(
                    Key = formKey,
                    UpdateExpression="SET couponCodes_used.#code.responses = list_append(if_not_exists(couponCodes_used.#code.responses, :empty_list), :responseId)",
                    ExpressionAttributeNames={
                        "#code": code
                    },
                    ExpressionAttributeValues = {
                        ":responseId": [responseId],
                        ":empty_list": []
                    },
                    ConditionExpression="attribute_exists(couponCodes_used.#code.responses)"
                )
        else:
            formsCollection.update_item(
                Key = formKey,
                UpdateExpression="SET couponCodes_used.#code = :couponCodeValue",
                ExpressionAttributeNames={
                    "#code": code
                },
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