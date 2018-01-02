# GCMW-CFF-LAMBDA
Lambda function used for GCMW CFF (forms framework).

# Setup
workon gcmw-cff-lambda
pip install -r requirements.txt -t .
Zip file and upload to lambda

# other commands

pip install pymongo -t .


aws lambda add-permission --function-name arn:aws:lambda:us-east-2:870467738435:function:gcmw-cff-render-form:DEV --source-arn 'arn:aws:execute-api:us-east-2:870467738435:ajd5vh06d8/*/*/gcmw-cff-render-form' --principal apigateway.amazonaws.com --statement-id 5ec070ac-b78f-4722-8572-44bfc618b4e4 --action lambda:InvokeFunction

aws lambda add-permission --function-name arn:aws:lambda:us-east-2:870467738435:function:gcmw-cff-render-form:${stageVariables.alias} --source-arn 'arn:aws:execute-api:us-east-2:870467738435:ajd5vh06d8/*/*/gcmw-cff-render-form' --principal apigateway.amazonaws.com --statement-id 5ec070ac-b78f-4722-8572-44bfc618b4e4 --action lambda:InvokeFunction

gcmw-cff-render-form:${stageVariables.alias}

action=getForm&id=5a3bdfd5059638058c8ef478