from http import HTTPStatus
import json
import os

from aws_lambda_powertools.logging.logger import Logger
from aws_lambda_powertools.utilities import parameters
import psycopg2

logger = Logger()

db_login = json.loads(parameters.get_secret(os.environ.get("RDS_SECRET")))

connection = psycopg2.connect(
    user=db_login["username"], password=db_login["password"],
    host=os.environ.get("DB_HOST"), database=os.environ.get("DB_NAME")
)

@logger.inject_lambda_context(log_event=True)

def lambda_handler(event, context):
    if ((params := event["queryStringParameters"]) is None
        or "meta" not in params
        or "pathway" not in params
        ):
        return {"statusCode": HTTPStatus.BAD_REQUEST}
        
    sql = "SELECT tissue FROM gsea WHERE varname = %s AND pathway = %s AND pvalue <= 0.05 AND pvalue is not null ORDER BY pvalue"
    
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, (params["meta"], params["pathway"]))
            result = cursor.fetchall()
            
    return {
        "statusCode": HTTPStatus.OK,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(result)
    }
