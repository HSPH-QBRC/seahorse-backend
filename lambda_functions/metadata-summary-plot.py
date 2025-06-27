from http import HTTPStatus
import json
import os

from aws_lambda_powertools.logging.logger import Logger
from aws_lambda_powertools.utilities import parameters
import psycopg2

import numpy as np

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
    try: 
        if ((params := event["queryStringParameters"]) is None
            or "category_a" not in params
            or "tissue" not in params
            ):
            return {"statusCode": HTTPStatus.BAD_REQUEST}
            
        category_a = params["category_a"]
        tissue = params["tissue"]
        
        comparison = "" if "comparison" not in params else params["comparison"]
        
        if comparison == "" or comparison == "m2m":
            sql = "SELECT DISTINCT gtex_id, value from metadata WHERE varname = %s AND tissue = %s AND value is not null"
        else:
            sql = "SELECT DISTINCT m1.gtex_id, exp.level FROM gene_expression AS exp JOIN metadata as m1 ON m1.gtex_id = exp.gtex_id WHERE exp.ensembl_id = %s AND m1.tissue = %s AND exp.level is not null"

        def barchart(data):
            categoryArr = []
            categoryCount = {}
            for row in data:
                if isinstance(row[1], float):
                    cat = '{:.2f}'.format(row[1])
                else: 
                    cat = row[1]
                if(cat not in categoryArr):
                    categoryArr.append(cat)
                    categoryCount[cat] = 1
                else:
                    categoryCount[cat] += 1
                        
            countArr = []
            for row in categoryCount:
                temp = {
                    "name": str(row),
                    "count": categoryCount[row]
                }
                countArr.append(temp)   
            return countArr
            
        def histogram(data):
            temp_data = []
            for row in data:
                temp_data.append(float(row[1]))

            hist, bins = np.histogram(temp_data, bins=20)
            
            my_bin = bins.tolist()
            my_hist = hist.tolist()
            
            d3_bin = []
            for i in range(len(my_bin) - 1):
                temp = {
                    "x0": my_bin[i],
                    "x1": my_bin[i+1],
                    "count": my_hist[i]
                }
                d3_bin.append(temp)
            
            return {"data": d3_bin}

        
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, (category_a, tissue))
                result = cursor.fetchall()
                
                if comparison != "":
                    final_result = histogram(result)
                else:
                    final_result = barchart(result)
                

        return {
            "statusCode": HTTPStatus.OK,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(final_result)
        }

    except Exception as e:
        logger.error(f"Error occurred: {e}")
        return {
            "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }
