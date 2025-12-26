import sqlite3  
import os  
from skeleton.sql_value import extract_values, extract_column_and_value


def check_value_in_any_table(column_name, value, db_id, db_path="your_database"):  
    database_path = os.path.join(db_path, f"{db_id}/{db_id}.sqlite")  
    conn = sqlite3.connect(database_path)  
    cursor = conn.cursor()  
    
    try:  
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")  
        tables = cursor.fetchall()  

        for (table_name,) in tables:  
            cursor.execute(f"PRAGMA table_info('{table_name}')")  
            columns = cursor.fetchall() 
           
            if any(column[1].lower() == column_name.lower() for column in columns):  
               
                value = value.replace("''", "'")
                query = f"SELECT 1 FROM '{table_name}' WHERE \"{column_name}\"= ? LIMIT 1"  
                cursor.execute(query, (value,))
                if cursor.fetchall(): 
                    # print("#####") 
                    print(f"The value '{value}' exists in column '{column_name}' in table '{table_name}'.") 
                    return 1  
            # print("\n")
        print(f"The value '{value}' does not exist in column '{column_name}' in any table.")    
        return 0  
    except Exception as e:  
        return 0  

    finally:  
       
        cursor.close()  
        conn.close()  

def check_value(item,bird_database):
    
    
    err_pred = item.get('err_pred','')
    db_id = item.get('db_id','')
    
    err_pred = err_pred.replace("`", "\"")
    values = extract_values(err_pred)
    # values: ['directed_by = Ben Jones']
    extracted_conditions = extract_column_and_value(values)              
    
    value_res = 1  

    
    for column, value in extracted_conditions:  
        
        if value=='':
            continue  
        if column is not None:  
            value_res = check_value_in_any_table(column, value, db_id,  db_path = bird_database)  
            if value_res == 0:  
                return 0  
    return 1
    