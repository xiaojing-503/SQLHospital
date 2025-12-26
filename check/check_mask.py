
from skeleton.sql_skeleton import get_sql_skeleton,get_sql_schema
from skeleton.sql_value import extract_values, extract_column_and_value
from skeleton.mapping import get_table_column_value
from utils.get_sql_schema_prompt import format_database_schema
from generate_sql import question_schema_full_skeletion_sql, question_schema_new_sql
from utils.get_full_schema_prompt import parse_schema_to_string
from check.check_sql_result import compare_sql_results,compute_report,get_system_error_desc

def process_schema_skeleton(item,database_file):
    err_pred = item.get('err_pred','')
    db_id = item.get('db_id','')
    try:
        full_schema = item['schema_sequence']  
        schema=parse_schema_to_string(full_schema)
    except:
        schema=item['full_schema']  
    err_pred = err_pred.replace("`", "\"")
    values = extract_values(err_pred)
    skeleton = get_sql_skeleton(err_pred)  
    sql_schemas = get_sql_schema(err_pred)  
    schema_mapping = get_table_column_value(database_file, db_id, sql_schemas, values)  
    new_schema = format_database_schema(schema_mapping)  
    
    return schema,skeleton,new_schema


def check_mask(item, database_file):
    timeout = 5
    
    full_schema, skeleton, new_schema = process_schema_skeleton(item, database_file)
    item['full_schema'] = full_schema  
    item['new_schema'] = new_schema
    item['skeleton'] = skeleton
    
    question = item.get('question', '')
    sql1 = question_schema_full_skeletion_sql(question, full_schema, skeleton)
    sql2 = question_schema_new_sql(question, new_schema)
    
    item['sql1'] = sql1
    item['sql2'] = sql2
    
    sql_initial = item.get('err_pred', '')
    db_id = item.get('db_id', '')
    
    comparison_result1 = compare_sql_results(database_file, db_id, sql_initial, sql1, timeout)
    comparison_result2 = compare_sql_results(database_file, db_id, sql_initial, sql2, timeout)
    
    item['err_type1'] = comparison_result1
    item['err_type2'] = comparison_result2
    
    if comparison_result1 != 'correct' or comparison_result2 != 'correct':
        return 0,item
        
    return 1,item

