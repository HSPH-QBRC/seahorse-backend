## Lambda Function Setup
There are **11 Lambda functions** required for the Seahorse backend API, each serving a specialized data endpoint. The source code for each function can be found in here [`lambda_functions`](./).

**The required Lambda functions are:**
1. `ensembl2symbol`
2. `gene2gene`
3. `gene2metadata`
4. `gsea-tissue-list`
5. `gsea`
6. `metadata-desc`
7. `metadata-summary-plot`
8. `metadata2gene`
9. `metadata2metadata`
10. `summary-plot`
11. `gsea-download-table`

### Function Configuration
- **Function name:** `ensembl2symbol`
- **Runtime:** `Python 3.9`
- **Architecture:** `x86_64`
- **Execution role:**  `lambda_role`
  Use an existing role that includes the following managed and custom policies:
  - **AWSLambdaVPCAccessExecutionRole:** Allows the Lambda function to run inside your VPC, enabling network connectivity to resources such as your RDS database.
  - **read-secrets:** A custom policy that grants permission to retrieve credentials and other sensitive data from AWS Secrets Manager.

- **Function URL:** `Enabled`
- **Auth type:** `AWS_IAM`

#### Networking (VPC configuration)

- **VPC:** `Enabled` (choose the VPC created for this project)
- **Subnets:** Select the private subnets associated with your database
- **Security groups:** Use the default or one that allows outbound DB access

---
### API Gateway Trigger Setup

This Lambda function should be integrated with **API Gateway** to provide accessible HTTP endpoints.

- **Intent:** `Create a new API`
- **API type:** `HTTP API`
- **Security:** `IAM authentication`
- **CORS:** Enable to allow frontend/browser calls (Yes)
 
#### Adding Routes

After the API is set up:
- In API Gateway, under **Routes**, add:
    - `/ensembl2symbol`
    - `/summary`
- Attach these routes to the Lambda integration.
- **Custom Domain & API Mappings:**  
    If using a custom domain:
    - Select your API under API Mappings  
    - Stage: `default`
    - Path: `e2s` (so your endpoint would be `https://<domain>/e2s/ensembl2symbol`, for example)

---

### Lambda Layers

Add the following Lambda Layers to include required Python libraries:

- **AWSLambdaPowertoolsPythonV2**  
  ARN: `arn:aws:lambda:us-east-2:245514619755:layer:psycopg2-binary:1 `

- **psycopg2-binary**  
  ARN: `arn:aws:lambda:us-east-2:017000801446:layer:AWSLambdaPowertoolsPythonV2:20`

---

### Environment Variables

Configure these environment variables for your Lambda function (these support securely connecting to your database):

- **DB_HOST** : `seahorse-instance.cfasu6406b8a.us-east-2.rds.amazonaws.com  `
- **DB_NAME** : `postgres`
- **RDS_SECRET** : `seahorse-rds-credentials` 


### Create VPC Endpoint
To allow the Lambda functions running inside your VPC to access secrets in AWS Secrets Manager, you must create a **VPC interface endpoint** for Secrets Manager. Without this endpoint (or a NAT Gateway), Lambdas in private subnets will time out when trying to retrieve secrets.

- **Type** : `AWS service`
- **Services** : `com.amazonaws.us-east-2.secretsmanager`
- **VPC** : `vpc-00086dc0a6124673c (seahorse)`
- **Subnets** : `us-east-2a (use2-az1)` => `subnet-02a8a562a0adc6c9b`
                `us-east-2a (use2-az2)` => `subnet-041c0a235db9eb7df`
- **Security Groups** : `default`

