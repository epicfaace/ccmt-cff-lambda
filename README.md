# GCMW-CFF-LAMBDA
Lambda function used for GCMW CFF (forms framework).

# Setup (new) with Apex
5. Deploy!
apex deploy && apex invoke forms < event.json
apex deploy --alias DEV && apex invoke --alias DEV forms < event.json
# Dev / prod workflow
apex deploy --alias DEV
apex deploy --alias PROD

# other commands (old)
API gateway: DO:

cff_forms:DEV
cff_forms:PROD
cff_forms:${stageVariables.alias}

## Form admin:
Form List: https://lf2n0amabe.execute-api.us-east-2.amazonaws.com/dev/form?action=formList&apiKey=test
Form Responses: https://lf2n0amabe.execute-api.us-east-2.amazonaws.com/dev/form?action=formResponses&id=59dbf12b734d1d18c05ebd21

Edit Forms (POST): https://lf2n0amabe.execute-api.us-east-2.amazonaws.com/dev/form?action=formEdit&apiKey=test

## Form render:
Render Form: https://lf2n0amabe.execute-api.us-east-2.amazonaws.com/dev/form?action=formRender&id=59dbf12b734d1d18c05ebd21
Submit Form (POST): https://lf2n0amabe.execute-api.us-east-2.amazonaws.com/dev/form?action=formSubmit&id=59dbf12b734d1d18c05ebd21

IPN handler: https://ajd5vh06d8.execute-api.us-east-2.amazonaws.com/prod/gcmw-cff-render-form?action=ipn