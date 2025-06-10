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
        or "geneA" not in params
        or "tissue" not in params
        or "offset" not in params
        or "limit" not in params
        ):
        return {"statusCode": HTTPStatus.BAD_REQUEST}

    ##Query for table results
    sql = "SELECT DISTINCT expression_correlation.gene_b, ensembl2symbol.symbol, ensembl2symbol.entrez_id, expression_correlation.correlation FROM expression_correlation JOIN ensembl2symbol ON expression_correlation.gene_b = ensembl2symbol.ensembl_id WHERE expression_correlation.gene_a = %s AND expression_correlation.tissue = %s ORDER BY expression_correlation.correlation DESC LIMIT %s OFFSET %s"
    
    ##Query for Count
    sql_count = "SELECT COUNT(DISTINCT expression_correlation.gene_b) FROM expression_correlation JOIN ensembl2symbol ON expression_correlation.gene_b = ensembl2symbol.ensembl_id WHERE expression_correlation.gene_a = %s AND expression_correlation.tissue = %s"

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, (params["geneA"], params["tissue"], params["limit"], params["offset"]))
            limit = int(params["limit"])
            result = cursor.fetchmany(limit)
            cursor.execute(sql_count, (params["geneA"], params["tissue"]))
            count = cursor.fetchone()
            
    json_results = {
        "result": result,
        "count": count[0]
    }
            
    return {
        "statusCode": HTTPStatus.OK,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(json_results)
    }

