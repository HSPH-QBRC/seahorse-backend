# seahorse-backend

## AWS SAM CLI

[Docker](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-docker.html)

```shell
sam build
```
```shell
sam local invoke
```
```shell
sam local start-lambda
```

## Initial configuration
Enable data imports from S3 after a new Aurora cluster is created:
```postgresql
create extension aws_s3 cascade;
```

## Data import from S3
Make sure that gzip'ed S3 objects have the correct metadata set:
* Content-Encoding: gzip
* Content-Type: application/octet-stream or application/x-gzip
