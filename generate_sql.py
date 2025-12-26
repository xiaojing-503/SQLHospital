import argparse
from utils.get_response import get_response
from utils.prompt import question_schema_skeleton_instruction, question_schema_skeleton_inputs, question_schema_new_instruction, question_schema_new_inputs
from utils.read_json_file import read_json_file
from utils.save_json_file import save_json_file
from utils.process_llm_output_sql import format_sql_to_single_line
import json
import transformers,torch
import time


def question_schema_full_skeletion_sql(question,full_schema,skeleton):
    inputs = question_schema_skeleton_inputs.format(
        question=question,
        schema_full=full_schema,
        skeleton=skeleton
    )
    print(inputs)
    
    while True:
        try:
            sql = get_response(question_schema_skeleton_instruction, inputs)
            break 
        except Exception as e:
            time.sleep(3)
        
        
    sql = format_sql_to_single_line(sql)
    print(sql)
    print("\n")
    return sql

def question_schema_new_sql(question,new_schema):

    inputs = question_schema_new_inputs.format(
        question=question,
        schema_new=new_schema
    )
    print(inputs)
    
    while True:
        try:
            sql = get_response(question_schema_new_instruction, inputs)
            break 
        except Exception as e:
            time.sleep(3)     
    sql = format_sql_to_single_line(sql)
    print(sql)
    print("\n")
    return sql

