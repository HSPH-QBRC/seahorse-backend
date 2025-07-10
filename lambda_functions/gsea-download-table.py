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
        or "tissue" not in params
        ):
        return {"statusCode": HTTPStatus.BAD_REQUEST}
        
    sql = "SELECT g1.pathway, g1.pvalue, STRING_AGG(g2.tissue, ', ') AS tissues FROM gsea g1 JOIN gsea g2 ON g1.varname = g2.varname AND g1.pathway = g2.pathway WHERE g1.varname = %s AND g1.tissue = %s AND g1.pvalue IS NOT NULL AND g2.pvalue <= 0.05 AND g2.pvalue IS NOT NULL GROUP BY g1.pvalue, g1.pathway ORDER BY g1.pvalue"
    
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, (params["meta"], params["tissue"]))
            result = cursor.fetchall()
            
    json_results = {
        "result": result
    }
            
    return {
        "statusCode": HTTPStatus.OK,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(json_results)
    }
