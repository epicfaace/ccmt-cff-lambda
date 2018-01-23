# Setup
Instructions for initial setup with a new AWS account.
1. Create IAM user with the following custom policy:
```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "iam:CreateRole",
        "iam:CreatePolicy",
        "iam:AttachRolePolicy",
        "iam:PassRole",
        "lambda:GetFunction",
        "lambda:ListFunctions",
        "lambda:CreateFunction",
        "lambda:DeleteFunction",
        "lambda:InvokeFunction",
        "lambda:GetFunctionConfiguration",
        "lambda:UpdateFunctionConfiguration",
        "lambda:UpdateFunctionCode",
        "lambda:CreateAlias",
        "lambda:UpdateAlias",
        "lambda:GetAlias",
        "lambda:ListAliases",
        "lambda:ListVersionsByFunction",
        "logs:FilterLogEvents",
        "cloudwatch:GetMetricStatistics"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
```
2. Configure AWS profile with credentials from previous screen.
```aws configure --profile ccmt-cff-lambda```
AWS Access Key ID: prev screen
AWS Secret Access Key: prev screen
Default region name: us-east-1
Default output format: JSON
3. Use AWS profile with apex.
apex init --profile ccmt-cff-lambda
4. Add following to your project.json:
```
"profile": "ccmt-cff-lambda",
"environment": {
}
```
5. Add the following to the function.json (inside the app)
```
{
    "description": "NOVA APPROVAL REST API",
    "hooks":{
      "build": "pip install -r requirements.txt -t ."
    }
}
```
6. Sending mail
Add the following policy to the lambda function role:
Email sending role: http://www.wisdomofjim.com/blog/sending-an-email-from-aws-lambda-function-in-nodejs-with-aws-simple-email-service
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "ses:SendEmail",
                "ses:SendRawEmail"
            ],
            "Resource": "*"
        }
    ]
}
```
7. DynamoDB
Add the following policy (ccmt_cff_lambda_dynamodb):
```
{
    "Version": "2012-10-17",
    "Statement": [
         {
            "Effect": "Allow",
            "Action": [
                "DynamoDB:*"
            ],
            "Resource": [
                "arn:aws:dynamodb:us-east-1:131049698002:table/ccmt_cff_forms",
                "arn:aws:dynamodb:us-east-1:131049698002:table/ccmt_cff_centers",
                "arn:aws:dynamodb:us-east-1:131049698002:table/ccmt_cff_schemas",
                "arn:aws:dynamodb:us-east-1:131049698002:table/ccmt_cff_schemaModifiers",
                "arn:aws:dynamodb:us-east-1:131049698002:table/ccmt_cff_responses",
                "arn:aws:dynamodb:us-east-1:131049698002:table/ccmt_cff_forms/index/center-index"
            ]
        }
    ]
}
```
Create secondary index on ccmt_cff_forms on column center

apex deploy

# Set up API gateway

apex deploy --alias DEV
apex deploy --alias PROD

CORS, Lambda proxy:
cff_forms:${stageVariables.alias}

Deployment stages dev and prod:
stageVariables: alias=DEV and alias=PROD

Deploy API.


# new policies
## ccmt_cff_dev_lambda_db
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "DynamoDB:*"
            ],
            "Resource": [
                "arn:aws:dynamodb:us-east-1:131049698002:table/cff_dev.forms",
                "arn:aws:dynamodb:us-east-1:131049698002:table/cff_dev.centers",
                "arn:aws:dynamodb:us-east-1:131049698002:table/cff_dev.schemas",
                "arn:aws:dynamodb:us-east-1:131049698002:table/cff_dev.schemaModifiers",
                "arn:aws:dynamodb:us-east-1:131049698002:table/cff_dev.responses",
                "arn:aws:dynamodb:us-east-1:131049698002:table/cff_dev.forms/index/center-index"
            ]
        }
    ]
}
## ccmt_cff_prod_lambda_db
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "DynamoDB:*"
            ],
            "Resource": [
                "arn:aws:dynamodb:us-east-1:131049698002:table/cff_prod.forms",
                "arn:aws:dynamodb:us-east-1:131049698002:table/cff_prod.centers",
                "arn:aws:dynamodb:us-east-1:131049698002:table/cff_prod.schemas",
                "arn:aws:dynamodb:us-east-1:131049698002:table/cff_prod.schemaModifiers",
                "arn:aws:dynamodb:us-east-1:131049698002:table/cff_prod.responses",
                "arn:aws:dynamodb:us-east-1:131049698002:table/cff_prod.forms/index/center-index"
            ]
        }
    ]
}
# CCMT_CFF_lambda_logs 
# ccmt_ses_access

Create roles:

# ccmt_cff_dev_lambda

CCMT_CFF_lambda_logs 
ccmt_cff_dev_lambda_db 
ccmt-ses-access 

# ccmt_cff_prod_lambda

CCMT_CFF_lambda_logs 
ccmt_cff_prod_lambda_db 
ccmt-ses-access 


# DEV SETUP
1. Get dev access key.
```aws configure --profile ccmt-cff-lambda-dev
```

AWS Access Key ID: prev screen
AWS Secret Access Key: prev screen
Default region name: us-east-1
Default output format: JSON

# PRODUCTION