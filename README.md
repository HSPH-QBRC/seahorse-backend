# Seahorse Backend

This repository provides the backend setup and data-loading instructions for the Seahorse project. The process involves loading large biological datasets into a secure AWS RDS (PostgreSQL) database using EC2 and S3 as intermediaries. To enable secure and scalable communication between the frontend and backend, we use AWS Lambda functions as API endpoints that interface with the database and return data to the frontend.

## Overview

SEAHORSE leverages structured multi-omic datasets for hypothesis generation and validation. For security and compliance, data imports to the RDS instance are performed within a secure EC2 environment with connectivity to both the S3 bucket (where input files reside) and the RDS database.

## Deployment
Configure Terraform:
```shell
cd deployment/terraform
terraform init

Deploy the site:
```shell
terraform apply
```

## Cleanup
Delete the site:
```shell
terraform destroy
```

## Data Loading Workflow

1. **Copy Data Files to S3 Bucket**  
   Place all `.tsv.gz` data files into your S3 bucket (e.g., `seahorse-data-jq`).

2. **Launch an EC2 Instance**  
   - Ensure the EC2 instance has permissions (IAM role) to access the S3 bucket and to connect to the RDS PostgreSQL instance (security group rules).
   - SSH into the EC2 instance.

3. **Transfer SQL Scripts**  
   - Upload `init.sql` and `import.sql` to the EC2 instance (e.g., with `scp` or S3).

4. **Run Initialization Script**  
   This creates the necessary tables in your RDS PostgreSQL database:

   ```sh
   psql -h <rds-endpoint> -U <db-username> -d <db-name> -f init.sql
   ```

5. **Run Import Script**
   Import all data from S3 into the created tables:

   ```sh
   psql -h <rds-endpoint> -U <db-username> -d <db-name> -f import.sql
   ```


## API & Lambda Integration

To allow the frontend to communicate securely with the backend database, you must set up AWS Lambda functions to serve as API endpoints.

For detailed instructions on setting up the Lambda functions, see  
[How to create Lambda functions](./lambda_functions/how-to-create-lambda-func.md).
