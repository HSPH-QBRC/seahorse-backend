# seahorse-backend

## Initial configuration
Enable data imports from S3 after a new Aurora cluster is created:
```postgresql
create extension aws_s3 cascade;
```
