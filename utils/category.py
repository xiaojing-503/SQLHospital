import json
import sqlite3
import os
import re

from utils.process_data import from_column_to_table, no_such_table

def read_json_file(file_path):  
    with open(file_path, 'r', encoding='utf-8') as file:  
        data = json.load(file)  
    return data  

def save_json_file(output_file,data):
    with open(output_file, 'w', encoding='utf-8') as final_file:  
        json.dump(data, final_file, ensure_ascii=False, indent=4)  

def execute_sql(database_name, sql):
    try:
        conn = sqlite3.connect(database_name)
        cursor = conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        conn.close()
        return result
    except sqlite3.Error as e:
        return f"SQLite error: {e}"
    
def get_system_error_desc(database_path, db_id, sql, timeout=5):
    database_name = os.path.join(database_path, db_id, f"{db_id}.sqlite")
    print(f"connect: {database_name}")

    try:
        result = execute_sql(database_name, sql)
        

        if isinstance(result, str):
            match = re.search(r'SQLite error: (.+)', result)
            if match:
                result = match.group(1)
            print(f"{result}")
            return result
        return ""  # 正常查询结果，返回空字符串

    except Exception as e:
        return "timeout"
    

def extract_func_from_desc(err_desc):

    function_pattern = re.compile(r'no such function: (\w+)')
   
    match = function_pattern.search(err_desc)
    if match:
        func = match.group(1)
        return func
    return None   

def get_tips(item,desc,db_path):
        
    tips=""
    if "no such table:" in desc:
        tips=no_such_table(item,desc,db_path)

    elif "no such column:" in desc:
        tips=from_column_to_table(item,desc,db_path)
    elif "no such function:" in desc:
        func=extract_func_from_desc(desc)
        tips=f"The function '{func}' doesn't exsit, please cancel the use.\n"
    elif "syntax error" in desc:
        tips="Ensure all table and column names are correctly spelled, check for proper use of SQL keywords, and verify that all parentheses and quotation marks are properly closed.\n"
    elif "misuse of" in desc:
        tips="Ensure that the aggregate function is used correctly within a GROUP BY clause or in a SELECT statement without other non-aggregate columns.\n"
    elif "SELECTs to the left and right of EXCEPT do not have the same number of result columns" in desc:
        tips="Ensure that the SELECT statements on both sides of the EXCEPT operator return the same number of columns with compatible data types.\n"
    else:
        tips=""
    return tips
