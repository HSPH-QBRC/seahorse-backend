## ensembl2symbol lambda function
Function name: ensembl2symbol
Runtime: Python 3.9
Architecture: x86_64
Execution role: Use existing role / lambda-role

Functional URL: Enabled
Auth type: AWS_IAM

VPC: Enabled
VPC: Choose the one created for the current project
Subnets: Choose the ones created for the current project
Security groups: default

### Add trigger
Intent: Create a new API
API type: HTTP API
Security: IAM
CORS: Yes

### Add routes
From Triggers > click on API Gateway > Routes
Add routes for "/ensembl2symbol" and "/summary"
Attach Integration to the API
Add to Custom domain > Configure API Mappings
- select API
- staging: default
- path : e2s

## Add layers
AWSLambdaPowertoolsPythonV2 ARN: arn:aws:lambda:us-east-2:245514619755:layer:psycopg2-binary:1
psycopg2-binary ARN: arn:aws:lambda:us-east-2:017000801446:layer:AWSLambdaPowertoolsPythonV2:20

## Add Environmental Variables
DB_HOST : seahorse-instance.cfasu6406b8a.us-east-2.rds.amazonaws.com
DB_NAME : postgres
RDS_SECRET : seahorse-rds-credentials
user : postgres
password : E+OilQ13hMdg9?_m0U[9Bo+jUhtI

connection = psycopg2.connect(
    user=os.environ.get("USER"),
    password=os.environ.get("PASSWORD"),
    host=os.environ.get("DB_HOST"), 
    database=os.environ.get("DB_NAME")
)