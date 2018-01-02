# GCMW-CFF-LAMBDA
Lambda function used for GCMW CFF (forms framework).

# Setup
workon gcmw-cff-lambda
pip install -r requirements.txt -t .
Zip file and upload to lambda

# Setup (new) with apex

aws configure --profile ashwin-cff-lambda
(us-east-2)

apex init --profile ashwin-cff-lambda

AWS_SDK_LOAD_CONFIG=1
apex deploy

apex deploy && apex invoke forms < event.json
apex deploy --alias DEV && apex invoke --alias DEV forms < event.json
# Dev / prod workflow
apex deploy --alias DEV
apex deploy --alias PROD

# other commands (old)
API gateway: DO:

GCMW_CFF_forms:DEV
GCMW_CFF_forms:PROD
GCMW_CFF_forms:${stageVariables.alias}

gcmw-cff-render-form:${stageVariables.alias}

## Form admin:
Form List: https://ajd5vh06d8.execute-api.us-east-2.amazonaws.com/dev/gcmw-cff-render-form?action=formList&apiKey=test
Form Responses: https://ajd5vh06d8.execute-api.us-east-2.amazonaws.com/dev/gcmw-cff-render-form?action=formResponses&id=59dbf12b734d1d18c05ebd21

Edit Forms (POST): https://ajd5vh06d8.execute-api.us-east-2.amazonaws.com/dev/gcmw-cff-render-form?action=formEdit&apiKey=test

## Form render:
Render Form: https://ajd5vh06d8.execute-api.us-east-2.amazonaws.com/dev/gcmw-cff-render-form?action=formRender&id=59dbf12b734d1d18c05ebd21
Submit Form (POST): https://ajd5vh06d8.execute-api.us-east-2.amazonaws.com/dev/gcmw-cff-render-form?action=formSubmit&id=59dbf12b734d1d18c05ebd21