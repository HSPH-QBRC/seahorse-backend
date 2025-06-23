from http import HTTPStatus
import json
import os

from aws_lambda_powertools.logging.logger import Logger
from aws_lambda_powertools.utilities import parameters
import psycopg2

logger = Logger()

# db_login = json.loads(parameters.get_secret(os.environ.get("RDS_SECRET")))

# connection = psycopg2.connect(
#     user=db_login["username"], password=db_login["password"],
#     host=os.environ.get("DB_HOST"), database=os.environ.get("DB_NAME")
# )

connection = psycopg2.connect(
    user=os.environ.get("USER"),
    password=os.environ.get("PASSWORD"),
    host=os.environ.get("DB_HOST"), 
    database=os.environ.get("DB_NAME")
)

@logger.inject_lambda_context(log_event=True)
def lambda_handler(event, context):
    if ((params := event["queryStringParameters"]) is None
        or "category_a" not in params
        or "offset" not in params
        or "limit" not in params
        or "meta" not in params
        or "tissue" not in params
        ):
        return {"statusCode": HTTPStatus.BAD_REQUEST}

    ##Query for table results
    sql = "SELECT m2e.varname, m2e.ensembl_id, m2e.test, m2e.test_statistic, m2e.pvalue FROM metadata2expression AS m2e JOIN data_dictionary AS dd ON dd.varname = m2e.varname WHERE dd.varmeta = %s AND m2e.ensembl_id = %s AND m2e.tissue = %s AND test_statistic != '-Infinity' AND test_statistic != 'Infinity' AND m2e.pvalue is not null ORDER BY m2e.pvalue LIMIT %s OFFSET %s"

    ##Query for Count 
    sql_count = "SELECT COUNT(*) FROM metadata2expression AS m2e JOIN data_dictionary AS dd ON dd.varname = m2e.varname WHERE dd.varmeta = %s AND m2e.ensembl_id = %s AND m2e.tissue = %s AND test_statistic != '-Infinity' AND test_statistic != 'Infinity' AND m2e.test != 'None' AND m2e.pvalue IS NOT NULL"
    
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, (params["meta"], params["category_a"], params["tissue"], params["limit"], params["offset"]))
            limit = int(params["limit"])
            result = cursor.fetchmany(limit)
            
            cursor.execute(sql_count, (params["meta"], params["category_a"], params["tissue"]))
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

