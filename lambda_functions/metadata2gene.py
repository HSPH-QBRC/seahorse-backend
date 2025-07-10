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
        or "category_a" not in params
        or "offset" not in params
        or "limit" not in params
        or "tissue" not in params
        ):
        return {"statusCode": HTTPStatus.BAD_REQUEST}

    ##Query for table results"
    sql = "SELECT varname, ensembl_id, test, test_statistic, pvalue FROM metadata2expression WHERE varname = %s AND tissue = %s AND test_statistic != '-Infinity' AND test_statistic != 'Infinity' AND test != 'None' AND pvalue is not null ORDER BY pvalue LIMIT %s OFFSET %s"

    
    # ##Query for Count 
    sql_count = "SELECT COUNT(*) FROM metadata2expression WHERE varname = %s AND tissue = %s AND test_statistic != '-Infinity' AND test_statistic != 'Infinity' AND test != 'None' AND pvalue IS NOT NULL AND pvalue != 'nan'"
    
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, (params["category_a"], params["tissue"], params["limit"], params["offset"]))
            limit = int(params["limit"])
            result = cursor.fetchmany(limit)
            
            cursor.execute(sql_count, (params["category_a"], params["tissue"]))
            count = cursor.fetchmany(1)
            
    json_results = {
        "result": result,
        "count": count[0][0]
    } 
    
    return {
        "statusCode": HTTPStatus.OK,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(json_results)
    }

