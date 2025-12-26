from utils.prompt import result_correction_instruction_skeleton,result_correction_inputs_skeleton

from utils.get_response import get_response
import time
from utils.process_llm_output_sql import format_sql_to_single_line
from utils.prompt2 import instruction2,inputs2,instruction3,inputs3



def correct_result(item):
    question = item.get('question','')
    sql1_schema = item.get('sql1_schema','')
    sql2_skeleton = item.get('sql2_skeleton','')
    sql_pred=item.get('err_pred','')
    schema=item.get('full_schema','')
    err_type1=item.get('err_type1','')
    err_type2=item.get('err_type2','')
    keys=item.get('schema_enhance','')
    # 1
    if err_type1 == "correct" and err_type2 != "correct":
  
        result_inputs = result_correction_inputs_skeleton.format(err_pred=sql_pred,question=question,schema_new=sql1_schema,keys=keys)

        print('instruction:',result_correction_instruction_skeleton)
        print('inputs:',result_inputs)
        while True:
            try:
                sql = get_response(result_correction_instruction_skeleton, result_inputs)
                sql = format_sql_to_single_line(sql)
                print('sql:', sql)
                break  
            except Exception as e:
                time.sleep(60)
        # sql=item.get('sql_new','')
    # 2
    elif err_type1 != "correct" and err_type2 == "correct":
        result_inputs = inputs2.format(question=question,schema=sql1_schema,keys=keys,skeleton=sql2_skeleton)

        print('instruction:',instruction2)
        print('inputs:',result_inputs)
        while True:
            try:
                sql = get_response(instruction2, result_inputs)
                sql = format_sql_to_single_line(sql)
                print('sql:', sql)
                break 
            except Exception as e:
                time.sleep(60)
        # sql=item.get('sql_new','')
   
    else:
        
        result_inputs = inputs3.format(pred=sql_pred,question=question,full_schema=schema)
        print('instruction:',instruction3)
        print('inputs:',result_inputs)
        while True:
            try:
                sql = get_response(instruction3, result_inputs)
                sql = format_sql_to_single_line(sql)
                print('sql:', sql)
                break  
            except Exception as e:
                time.sleep(60)
        
    return sql


