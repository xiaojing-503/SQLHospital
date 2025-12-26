from utils.prompt import empty_correction_instruction,empty_correction_inputs,empty_correction_instruction_simple,empty_correction_inputs_simple
from utils.get_response import get_response
import time
import os
import re
from utils.process_llm_output_sql import format_sql_to_single_line
from skeleton.sql_value import extract_values, extract_column_and_value
from utils.correct_value import find_similar_values_in_all_tables
from utils.prompt import generate_values_instruction, generate_values_inputs
import ast
import sqlite3
import json

def check_value_in_db(db_path, column, value):
    
    try:
        column = column.lower()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]

        for table in tables:
           
            cursor.execute(f"PRAGMA table_info({table});")
            columns = [row[1].lower() for row in cursor.fetchall()]
            # print(columns)

            if column in columns:
                
                query = f"SELECT 1 FROM {table} WHERE {column} = ? LIMIT 1;"
                cursor.execute(query, (value,))
                result = cursor.fetchone()

                if result:  
                    conn.close()
                    return True

        conn.close()
        return False  
    except Exception as e:
        return False

def extract_list_from_string(llm_output):
  
    
    match = re.search(r"\[.*?\]", llm_output)
    if not match:
        return []  
    
    extracted_str = match.group()  

    try:
        return json.loads(extracted_str)
    except json.JSONDecodeError:
        pass  

    try:
        return ast.literal_eval(extracted_str)
    except (ValueError, SyntaxError):
        print(f"Warning: Failed to parse extracted string: {extracted_str}")
        return []  

def correct_empty(item,database_path):
    err_pred = item.get('err_pred','')
    db_id = item.get('db_id','')
    question = item.get('question','')
    db_path = os.path.join(database_path, db_id, f"{db_id}.sqlite")

    vvalues=''

    # LIKE Matching
    values = extract_values(err_pred)
    # values: ['directed_by = Ben Jones']
    extracted_conditions = extract_column_and_value(values)  
    # [('hand', '+')]
    # print(extracted_conditions)  
    for column, value in extracted_conditions:  
        if value=='':
            continue  
        if column is not None:  
            # print(value)
            similar_values = find_similar_values_in_all_tables(db_path, value, case_sensitive=False)
            for table, col, val in similar_values:
                vvalues += f"[`{col}` = '{val}']; "
    print("vvalues like:",vvalues)  

    # LLM Expansion
    for column, value in extracted_conditions:  
        print(column,value)
        if value=='':
            continue  
        if column is not None:
            expansion_instruction=generate_values_instruction
            expansion_inputs=generate_values_inputs.format(question=question,value=value)
            # LLM ["F", "woman"]”
            value_res = get_response(expansion_instruction,expansion_inputs)
            value_res = extract_list_from_string(value_res)
            # print("??",value_res)
            # # string_array = '["F", "woman"]'
            # value_res = ast.literal_eval(value_res)
            print("value_res:",value_res)

            for val in value_res:
                if check_value_in_db(db_path,column,val):
                    print("yes!")
                    vvalues += f"[`{column}` = '{val}']; "
    print("vvalues llm: ",vvalues)    
    empty_inputs = empty_correction_inputs.format(err_pred=err_pred,question=question,values=vvalues)
   
    while True:
        try:
            sql = get_response(empty_correction_instruction, empty_inputs)
            sql = format_sql_to_single_line(sql)
            print('sql:', sql)
            break  
        except Exception as e:
            time.sleep(3)

    return sql


