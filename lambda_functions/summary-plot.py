from http import HTTPStatus
import json
import os

from aws_lambda_powertools.logging.logger import Logger
from aws_lambda_powertools.utilities import parameters
import psycopg2

import matplotlib.pyplot as plt
import numpy as np
import io
import boto3
import base64

logger = Logger()

db_login = json.loads(parameters.get_secret(os.environ.get("RDS_SECRET")))

connection = psycopg2.connect(
    user=db_login["username"], password=db_login["password"],
    host=os.environ.get("DB_HOST"), database=os.environ.get("DB_NAME")
)

@logger.inject_lambda_context(log_event=True)
def lambda_handler(event, context):
    try: 
        if ((params := event["queryStringParameters"]) is None
            or "category_a" not in params
            or "category_b" not in params
            # or "comparison" not in params
            ):
            return {"statusCode": HTTPStatus.BAD_REQUEST}
        
        category_a = params["category_a"]
        category_b = params["category_b"]
        
        input_type = {}
        def type_check(name):
            if(name.startswith("ENSG") or metadata_dict[name]["type"] == "decimal" or metadata_dict[name]["type"] == "integer"):
                return "numeric"
            else:
                return "categoric"
                
        def scatterplot(numeric1, numeric2, num1_desc, num2_desc):
            plt.clf()
            if params["comparison"] == "m2m":
                if(metadata_dict[numeric1]["meta"] == "library" and metadata_dict[numeric2]["meta"] == "library"):
                    query = "SELECT t1.gtex_id, t1.value, t2.value FROM metadata_data_records AS t1 JOIN metadata_data_records AS t2 ON t1.gtex_id = t2.gtex_id WHERE t1.varname <> t2.varname AND t1.varname = '{0}' AND t2.varname = '{1}' AND t1.value IS NOT null AND t2.value IS NOT null".format(numeric1, numeric2)
                elif (metadata_dict[numeric1]["meta"] == "phenotype" and metadata_dict[numeric2]["meta"] == "phenotype"):
                    query = "SELECT t1.subject_id, t1.value, t2.value FROM phenotype_data_records AS t1 JOIN phenotype_data_records AS t2 ON t1.subject_id = t2.subject_id WHERE t1.varname <> t2.varname AND t1.varname = '{0}' AND t2.varname = '{1}' AND t1.value IS NOT null AND t2.value IS NOT null".format(numeric1, numeric2)
                else:
                    query = "SELECT mdr.gtex_id, mdr.value, pdr.value FROM phenotype_data_records AS pdr JOIN metadata_data_records AS mdr ON SPLIT_PART(mdr.gtex_id, '-', 2) = SPLIT_PART(pdr.subject_id, '-', 2) WHERE mdr.varname = '{0}' AND pdr.varname = '{1}' AND mdr.value is not null AND pdr.value is not null LIMIT 50".format(numeric1, numeric2)
            elif params["comparison"] == "g2g":
                query = "SELECT t1.sampid, t1.gene_expression AS gene_expression_1, t2.gene_expression AS gene_expression_2 FROM expression t1, expression t2 WHERE t1.sampid = t2.sampid AND t1.ensg = '{0}' AND t2.ensg = '{1}' AND t1.gene_expression is not null AND t2.gene_expression is not null".format(numeric1, numeric2)
            elif params["comparison"] == "m2g":
                if(metadata_dict[numeric1]["meta"] == "library"):
                    query = "SELECT t1.gtex_id, t1.value, t2.gene_expression FROM metadata_data_records AS t1 JOIN expression AS t2 ON t1.gtex_id = t2.sampid WHERE t1.varname = '{0}' AND t2.ensg = '{1}' AND t1.value IS NOT null AND t2.gene_expression IS NOT null".format(numeric1, numeric2)
                else:
                    query = "SELECT t1.subject_id, t1.value, t2.gene_expression FROM phenotype_data_records AS t1 JOIN expression AS t2 ON SPLIT_PART(t2.sampid, '-', 2) = SPLIT_PART(t1.subject_id, '-', 2) WHERE t1.varname = '{0}' AND t2.ensg = '{1}' AND t1.value IS NOT null AND t2.gene_expression IS NOT null".format(numeric1, numeric2)
            
 
            cursor.execute(query)
            result = cursor.fetchall()
            
            xArr = []
            yArr = []
            for x in result:
                xArr.append(float(x[1]))
                yArr.append(float(x[2]))
                
            plt.xlabel(num1_desc, fontsize=10)
            plt.ylabel(num2_desc, fontsize=10)

            x = np.array(xArr)
            y = np.array(yArr)
            plt.scatter(x, y, s=2, color='#69b3a2')
            
            # Save the plot to a PNG file
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            image_png = buffer.getvalue()

            # Encode the PNG image as base64
            image_base64 = base64.b64encode(image_png).decode()

            return image_base64
        
        def heatmap(categoric_a, categoric_b):
            if (metadata_dict[categoric_a]["meta"] == "library" and metadata_dict[categoric_b]["meta"] == "library"):
                heatmap_query = "SELECT t1.gtex_id, t1.value, t2.value FROM metadata_data_records AS t1 JOIN metadata_data_records AS t2 ON t1.gtex_id = t2.gtex_id WHERE t1.varname <> t2.varname AND t1.varname = '{0}' AND t2.varname = '{1}' AND t1.value IS NOT null AND t2.value IS NOT null".format(categoric_a, categoric_b)
               
            elif (metadata_dict[categoric_a]["meta"] == "phenotype" and metadata_dict[categoric_b]["meta"] == "phenotype"):
                heatmap_query = "SELECT t1.subject_id, t1.value, t2.value FROM phenotype_data_records AS t1 JOIN phenotype_data_records AS t2 ON t1.subject_id = t2.subject_id WHERE t1.varname <> t2.varname AND t1.varname = '{0}' AND t2.varname = '{1}' AND t1.value IS NOT null AND t2.value IS NOT null".format(categoric_a, categoric_b)
            else:
                if(metadata_dict[categoric_a]["meta"] == "library"):
                    heatmap_query = "SELECT mdr.gtex_id, mdr.value, pdr.value FROM phenotype_data_records AS pdr JOIN metadata_data_records AS mdr ON SPLIT_PART(mdr.gtex_id, '-', 2) = SPLIT_PART(pdr.subject_id, '-', 2) WHERE mdr.varname = '{0}' AND pdr.varname = '{1}' AND mdr.value is not null AND pdr.value is not null LIMIT 100".format(categoric_a, categoric_b)
                else:
                    heatmap_query = "SELECT mdr.gtex_id, mdr.value, pdr.value FROM phenotype_data_records AS pdr JOIN metadata_data_records AS mdr ON SPLIT_PART(mdr.gtex_id, '-', 2) = SPLIT_PART(pdr.subject_id, '-', 2) WHERE mdr.varname = '{0}' AND pdr.varname = '{1}' AND mdr.value is not null AND pdr.value is not null LIMIT 100".format(categoric_b, categoric_a)

            cursor.execute(heatmap_query)
            result = cursor.fetchall()
            
            xAxisArr = []
            yAxisArr = []
            annotations_list = []
            count_dict = {}
           
            for row in result:
                xValue = str(row[1])
                yValue = str(row[2])
                temp_obj = {
                    "name": row[0],
                    "xValue": xValue,
                    "yValue": yValue
                }
                annotations_list.append(temp_obj)
            
                if xValue not in xAxisArr:
                    xAxisArr.append(xValue)
                    
                if yValue not in yAxisArr:
                    yAxisArr.append(yValue)
                    
                temp_string = xValue + "_" + yValue
                if temp_string not in count_dict:
                    count_dict[temp_string] = 1
                else:
                    count_dict[temp_string] += 1
                    
            for i in xAxisArr:
                for j in yAxisArr:
                    temp_string = i + "_" + j
                    if temp_string not in count_dict:
                        count_dict[temp_string] = 0
                        temp_obj = {
                            "name": "",
                            "xValue": i,
                            "yValue": j
                        }
                        annotations_list.append(temp_obj)
                    
            return [annotations_list, count_dict]
            
        def boxplot(categoric, numeric):
            if params["comparison"] == "m2m":
                # boxplot_query = 'SELECT gtex_id, {0}, {1} FROM annotations WHERE {0} is not null AND {1} is not null'.format(numeric, categoric)
                if (metadata_dict[categoric]["meta"] == "library" and metadata_dict[numeric]["meta"] == "library"):
                    boxplot_query = "SELECT t1.gtex_id, t1.value, t2.value FROM metadata_data_records AS t1 JOIN metadata_data_records AS t2 ON t1.gtex_id = t2.gtex_id WHERE t1.varname <> t2.varname AND t1.varname = '{0}' AND t2.varname = '{1}' AND t1.value IS NOT null AND t2.value IS NOT null".format(numeric, categoric)
                elif (metadata_dict[categoric]["meta"] == "phenotype" and metadata_dict[numeric]["meta"] == "phenotype"):
                    boxplot_query = "SELECT t1.subject_id, t1.value, t2.value FROM phenotype_data_records AS t1 JOIN phenotype_data_records AS t2 ON t1.subject_id = t2.subject_id WHERE t1.varname <> t2.varname AND t1.varname = '{0}' AND t2.varname = '{1}' AND t1.value IS NOT null AND t2.value IS NOT null".format(numeric, categoric)
                    # boxplot_query = "SELECT t1.subject_id, t1.value, t2.value FROM phenotype_data_records AS t1 JOIN phenotype_data_records AS t2 ON t1.subject_id = t2.subject_id WHERE t1.varname = '{0}' AND t2.varname = '{1}' AND t1.value IS NOT null AND t2.value IS NOT null".format(categoric, numeric)
                else:
                    if (metadata_dict[categoric]["meta"] == "library"): ## AND numeric == "phenotype"
                        boxplot_query = "SELECT mdr.gtex_id, pdr.value, mdr.value FROM phenotype_data_records AS pdr JOIN metadata_data_records AS mdr ON SPLIT_PART(mdr.gtex_id, '-', 2) = SPLIT_PART(pdr.subject_id, '-', 2) WHERE mdr.varname = '{0}' AND pdr.varname = '{1}' AND mdr.value is not null AND pdr.value is not null LIMIT 1000".format(categoric, numeric)
                    elif (metadata_dict[categoric]["meta"] == "phenotype"): ## AND numeric == "library"
                        boxplot_query = "SELECT mdr.gtex_id, mdr.value, pdr.value FROM phenotype_data_records AS pdr JOIN metadata_data_records AS mdr ON SPLIT_PART(mdr.gtex_id, '-', 2) = SPLIT_PART(pdr.subject_id, '-', 2) WHERE mdr.varname = '{0}' AND pdr.varname = '{1}' AND mdr.value is not null AND pdr.value is not null LIMIT 1000".format(numeric, categoric)
                 
            elif params["comparison"] == "m2g":
                limit_num = '1000'
                if(metadata_dict[categoric]["meta"] == "phenotype"):
                    boxplot_query = "SELECT pdr.subject_id, exp.gene_expression, pdr.value, exp.ensg FROM phenotype_data_records AS pdr JOIN expression AS exp ON SPLIT_PART(pdr.subject_id, '-', 2) = SPLIT_PART(exp.sampid, '-', 2) WHERE exp.ensg = '{1}' AND pdr.varname = '{0}' AND pdr.value is not null AND exp.gene_expression is not null LIMIT {2}".format(categoric, numeric, limit_num)
                elif(metadata_dict[categoric]["meta"] == "library"):
                    boxplot_query = "SELECT mdr.gtex_id, exp.gene_expression, mdr.value, exp.ensg FROM metadata_data_records AS mdr JOIN expression AS exp ON SPLIT_PART(mdr.gtex_id, '-', 2) = SPLIT_PART(exp.sampid, '-', 2) WHERE exp.ensg = '{1}' AND mdr.varname = '{0}' AND mdr.value is not null AND exp.gene_expression is not null LIMIT {2}".format(categoric, numeric, limit_num)

            cursor.execute(boxplot_query)
            result = cursor.fetchall()
            
            box_plot_data = []
            main_data = {}
            
            
            for index in result:
                temp_obj = {
                    "name": index[0],
                    "key": index[2],
                    "value": index[1]
                }
                box_plot_data.append(temp_obj)
                
                if str(index[2]) not in main_data:
                    temp = []
                    temp.append(float(index[1]))
                    main_data[str(index[2])] = {
                    "arr": temp
                    }
                else:
                    # main_data[str(index[2])]["arr"].append(float(index[1]))
                    
                    ## Need to check for the reason for this check to make sure it is a number
                    # if str(index[1]).isdigit():
                    # temp = str(index[1])
                    # if temp.isnumeric():
                        main_data[str(index[2])]["arr"].append(float(index[1]))
                    # else:
                    #     main_data[str(index[2])]["arr"].append(index[1])
            
            def getBoxplotInfo(arr):
                if len(arr) == 0:
                    return {}
                    
                data_array = np.array(arr)
                np.sort(data_array)
            
                q1 = np.percentile(data_array, 25)
                q2 = np.percentile(data_array, 50)
                q3 = np.percentile(data_array, 75)
            
                iqr = q3 - q1
                
                # Determine lower and upper whiskers
                lower_whisker = data_array[data_array >= q1 - 1.5*iqr].min()
                upper_whisker = data_array[data_array <= q3 + 1.5*iqr].max()

                median = np.median(data_array)
                data_min, data_max = np.min(data_array), np.max(data_array)
                
                # return {"q1": q1, "q3": q3, "median": median, "interQuantileRange": iqr, "min": float(data_min), "max": float(data_max), "lower_whisker": float(lower_whisker), "upper_whisker": float(upper_whisker)}
                return {"q1": q1, "q3": q3, "median": median, "interQuantileRange": iqr, "min": float(lower_whisker), "max": float(upper_whisker), "lower_whisker": float(lower_whisker), "upper_whisker": float(upper_whisker)}

                
            final_result = []
            for key in main_data:
                val = getBoxplotInfo(main_data[key]["arr"])
                if bool(val):
                    temp = {
                        "key": key,
                        "value": val
                    }
                    final_result.append(temp)
                
            return {"boxPlotData": final_result}
            # return {"boxPlotData": box_plot_data}
            # return {"boxPlotData": result}
        
        with connection:
            with connection.cursor() as cursor:
                metadata_dict = {}
                #get Axis labels and data types
                if "ENSG" not in category_a and "ENSG" not in category_b:
                    sql_test = 'SELECT varname, vardesc, vartype, varmeta FROM data_dictionary WHERE data_dictionary.varname = %s OR data_dictionary.varname = %s'
                    cursor.execute(sql_test, (category_a, category_b))
                    result_metadata = cursor.fetchall()   
                    for x in result_metadata:
                        metadata_dict[x[0]] = {
                            "desc" : x[1].split(": ")[0],
                            "type" : x[2],
                            "meta" : x[3]
                        }
                elif "ENSG" not in category_a:
                    sql_test = 'SELECT varname, vardesc, vartype, varmeta FROM data_dictionary WHERE data_dictionary.varname = %s'
                    cursor.execute(sql_test, (category_a,))
                    result_metadata = cursor.fetchall()   
                    for x in result_metadata:
                        metadata_dict[x[0]] = {
                            "desc" : x[1].split(": ")[0],
                            "type" : x[2],
                            "meta" : x[3]
                        }
                    metadata_dict[category_b] = {
                            "desc" : "_",
                            "type" : "numeric",
                            "meta" : ""
                    }
                elif "ENSG" not in category_b:
                    sql_test = 'SELECT varname, vardesc, vartype, varmeta FROM data_dictionary WHERE data_dictionary.varname = %s'
                    cursor.execute(sql_test, (category_b,))
                    result_metadata = cursor.fetchall()  
                    for x in result_metadata:
                        metadata_dict[x[0]] = {
                            "desc" : x[1].split(": ")[0],
                            "type" : x[2],
                            "meta" : x[3]
                        }
                    metadata_dict[category_a] = {
                            "desc" : "_",
                            "type" : "numeric",
                            "meta" : ""
                    }
                else:
                    metadata_dict[category_a] = {
                            "desc" : str(category_a),
                            "type" : "numeric",
                            "meta" : ""
                    }
                    metadata_dict[category_b] = {
                            "desc" : str(category_b),
                            "type" : "numeric",
                            "meta" : ""
                    }
                
                input_type[category_a] = type_check(category_a)
                input_type[category_b] = type_check(category_b)
                
                boxplotdata = []
                count_data = {}
                if (input_type[category_a] == "numeric" and input_type[category_b] == "numeric"):
                    image_string = scatterplot(category_a, category_b, metadata_dict[category_a]["desc"], metadata_dict[category_b]["desc"])
                    return {
                        'statusCode': 200,
                        'headers': {
                            'Content-Type': 'text/plain'
                            },
                        'body': image_string
                        # 'body': {"one": category_a, "two": category_b}
                    }
                elif (input_type[category_a] == "categoric" and input_type[category_b] == "categoric"):
                    temp_data = heatmap(category_a, category_b)
                    data = temp_data[0]
                    count_data = temp_data[1]
                    
                    return {
                    "statusCode": HTTPStatus.OK,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"rows": data, "count_obj": count_data, "input_type": input_type})
                    }
                elif (input_type[category_a] == "numeric" and input_type[category_b] == "categoric") or (input_type[category_a] == "categoric" and input_type[category_b] == "numeric"):
                    ## category_a is catgoric, cat_b is numeric
                    if input_type[category_a] == "categoric":
                        boxplotdata = boxplot(category_a, category_b)
                    elif input_type[category_a] == "numeric":
                        boxplotdata = boxplot(category_b, category_a)
                    
                    return {
                    "statusCode": HTTPStatus.OK,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"boxplot": boxplotdata, "input_type": input_type})
                    }
  
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        return {
            "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }