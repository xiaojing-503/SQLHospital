from utils.prompt import ablation_system_correction_instruction,ablation_system_correction_inputs
from utils.get_response import get_response
import time
import os
from utils.process_llm_output_sql import format_sql_to_single_line
from check.check_sql_result import get_system_error_desc
from utils.category import get_tips

def correct_system(item,database_path):

    sql_schema = item.get('full_schema','')
    err_pred = item.get('err_pred','')
    db_id = item.get('db_id','')
    question = item.get('question','')

    err_desc = item.get('err_desc','')
    tips = get_tips(item,err_desc,database_path)
    err_desc = get_system_error_desc(database_path, db_id, err_pred)
    
    system_inputs = ablation_system_correction_inputs.format(question=question,schema_new=sql_schema,err_pred=err_pred,err_desc=err_desc,tips=tips)
    
    print(system_inputs)
    while True:
        try:
            sql = get_response(ablation_system_correction_instruction, system_inputs)
            sql = format_sql_to_single_line(sql)
            print('sql:', sql)
            break  
        except Exception as e:
            time.sleep(3)
    return sql

