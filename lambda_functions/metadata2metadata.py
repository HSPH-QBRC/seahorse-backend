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
        or "meta" not in params
        or "tissue" not in params
        ):
        return {"statusCode": HTTPStatus.BAD_REQUEST}

    ##Query for table results
    # sql = "SELECT category_a, category_b, test, test_statistic, pvalue FROM metadata2metadata WHERE category_a = %s AND test != 'None' AND pvalue IS NOT NULL AND pvalue != 'nan' ORDER BY pvalue LIMIT %s OFFSET %s"
    sql = "SELECT m2m.category_a, m2m.category_b, m2m.test, m2m.test_statistic, m2m.pvalue FROM metadata2metadata AS m2m JOIN data_dictionary AS dd ON dd.varname = m2m.category_b WHERE dd.varmeta = %s AND m2m.category_a = %s AND m2m.tissue = %s AND m2m.test != 'None' AND m2m.pvalue IS NOT NULL AND m2m.pvalue != 'nan' AND m2m.test_statistic != 'infinity' ORDER BY m2m.pvalue LIMIT %s OFFSET %s"
    
    ##Query for Count 
    sql_count = "SELECT COUNT(*) FROM metadata2metadata AS m2m JOIN data_dictionary AS dd ON dd.varname = m2m.category_b WHERE dd.varmeta = %s AND m2m.category_a = %s AND m2m.tissue = %s AND m2m.test != 'None' AND m2m.pvalue IS NOT NULL AND m2m.pvalue != 'nan' AND m2m.test_statistic != 'infinity'"
    
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

