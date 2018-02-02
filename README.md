# GCMW-CFF-LAMBDA
Lambda function used for GCMW CFF (forms framework).

# Setup (new) with Apex
5. Deploy!
apex deploy && apex invoke forms < event.json
apex deploy --alias DEV && apex invoke --alias DEV forms < event.json
# Dev / prod workflow
apex deploy forms --alias DEV
apex deploy forms --env prod --alias PROD
apex deploy forms --env beta --alias BETA

apex deploy copyTable --env devtableadmin

# other commands (old)
API gateway: DO:

CCMT_CFF_forms:DEV
CCMT_CFF_forms:PROD
cff_forms:${stageVariables.alias}

## Form admin:
Form List: https://l5nrf4co1g.execute-api.us-east-1.amazonaws.com/prod/forms?action=formList&apiKey=test
Form Responses: https://l5nrf4co1g.execute-api.us-east-1.amazonaws.com/prod/forms?action=formResponses&id=59dbf12b734d1d18c05ebd21

Edit Forms (POST): https://l5nrf4co1g.execute-api.us-east-1.amazonaws.com/prod/forms?action=formEdit&apiKey=test

## Form render:
Render Form: https://l5nrf4co1g.execute-api.us-east-1.amazonaws.com/prod/forms?action=formRender&id=59dbf12b734d1d18c05ebd21
Submit Form (POST): https://l5nrf4co1g.execute-api.us-east-1.amazonaws.com/prod/forms?action=formSubmit&id=59dbf12b734d1d18c05ebd21

IPN handler: https://l5nrf4co1g.execute-api.us-east-1.amazonaws.com/prod/forms?action=ipn