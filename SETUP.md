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
```aws configure --profile ccmt-dev-cff-lambda```
AWS Access Key ID: prev screen
AWS Secret Access Key: prev screen
Default region name: us-east-2
Default output format: JSON
3. Use AWS profile with apex.
apex init --profile ccmt-dev-cff-lambda
4. Add following to your project.json:
"profile": "ccmt-dev-cff-lambda"
"environment": {
}

apex deploy

# Set up API gateway

apex deploy --alias DEV
apex deploy --alias PROD

CORS, Lambda proxy:
cff_forms:${stageVariables.alias}

Deployment stages dev and prod:
stageVariables: alias=DEV and alias=PROD

Deploy API.