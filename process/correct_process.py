from utils.save_json_file import save_json_file
from utils.read_json_file import read_json_file
from skeleton.sql_skeleton import get_sql_skeleton,get_sql_schema
from skeleton.sql_value import extract_values
from skeleton.mapping import get_table_column_value
from utils.get_sql_schema_prompt import format_database_schema
import sqlite3
import re


def replace_special_characters_in_sql(file_path,save_path):

    content = read_json_file(file_path)
    for item in content:
        sql1=item['sql1']
        sql2=item['sql2']
       
        sql1 = sql1.replace("`", "\"")
        sql2 = sql2.replace("`", "\"")

        item['sql1']=sql1
        item['sql2']=sql2
    
    save_json_file(save_path,content)

import os
def get_all_columns_for_db(database_path, db_id, tables):
    database_name = os.path.join(database_path, db_id, f"{db_id}.sqlite")  
    
    columns = set()  

    try:  
        connection = sqlite3.connect(database_name)  
        cursor = connection.cursor()  

        for table in tables:  
            cursor.execute(f"PRAGMA table_info('{table}');")  
            column_info = cursor.fetchall()  

            for column in column_info:  
                columns.add(column[1])  

    except sqlite3.Error as e:  
        print(f"An error occurred: {e}")  

    finally:  
        if connection:  
            connection.close()  

    return columns  


def get_skeketon_schema(bird_file_path,file2,bird_database):
    
    data=read_json_file(bird_file_path)

    for item in data:  
        new_err_type = item['new_err_type'] 
        if new_err_type=='result':
            sql0 = item['err_pred']
            sql0 = sql0.replace("`", "\"")
            sql1 = item['sql1']
            sql1 = sql1.replace("`", "\"")
            sql2 = item['sql2']  
            sql2 = sql2.replace("`", "\"")
            
            db_id = item['db_id']  

            print(sql1)
            print(sql2)
            print("\n")

            values0 = extract_values(sql0)
            values1 = extract_values(sql1)

            values = list(set(values0 + values1))  

            sql_schemas0 = get_sql_schema(sql0)
            sql_schemas1 = get_sql_schema(sql1)

            tables = set(sql_schemas0[0]).union(sql_schemas1[0])  
            columns = set(sql_schemas0[1]).union(sql_schemas1[1])  
            # values = set(sql_schemas0[2]).union(sql_schemas1[2])

            sql_schemas = (tables, columns, values)



            schema_mapping = get_table_column_value(bird_database, db_id, sql_schemas, values)  
            new_schema = format_database_schema(schema_mapping) 

            skeleton2 = get_sql_skeleton(sql2)


        else:
            new_schema=''
            skeleton2=''

        item['sql1_schema']=new_schema
        item['sql2_skeleton']=skeleton2
        
    save_json_file(file2,data)

