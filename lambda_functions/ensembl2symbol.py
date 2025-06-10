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
    sql = 'SELECT DISTINCT ensembl_id, symbol FROM ensembl2symbol WHERE ensembl_id IS NOT null ORDER BY symbol'
    
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
  
    return {
        "statusCode": HTTPStatus.OK,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(result)
    }