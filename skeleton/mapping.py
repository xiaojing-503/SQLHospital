import sqlite3
import os


def get_column_table_mapping(database_name):
    connection = sqlite3.connect(database_name)
    
    column_to_table_mapping = {}

    try:
        cursor = connection.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info('{table_name}');")
            columns = cursor.fetchall()

            for col in columns:
                column_name = col[1].lower()  
                if column_name not in column_to_table_mapping:
                    column_to_table_mapping[column_name] = []
                column_to_table_mapping[column_name].append(table_name)

    finally:
        connection.close()

    return column_to_table_mapping

def map_columns_to_tables_and_values(sql_schema, extracted_values, column_to_table_mapping):
    tables, columns, _ = sql_schema  
    column_to_value = {}

    if len(columns) == 0 and len(extracted_values) == 0:
        for table in tables:  
            table_column_key = f'{table}:*' 
            column_to_value[table_column_key] = []  
        return column_to_value

    if len(extracted_values) == 0:
        for col in columns:  # Case insensitive match
            col = col.lower().strip()  
            if col in column_to_table_mapping:
                for table in column_to_table_mapping[col]:
                    table_column_key = f'{table}:{col}'
                    if table_column_key not in column_to_value:
                        column_to_value[table_column_key] = []

    else:
        for condition in extracted_values:
            operator = None
            if ' = ' in condition:
                column, value = condition.split(' = ', 1)  
                operator = '='
            elif ' != ' in condition:
                column, value = condition.split(' != ', 1)
                operator = '!='
            else:
                
                continue

            column = column.strip().lower()  
            value = value.strip()

            if column in [col.lower() for col in columns]:  
                if column in column_to_table_mapping:
                    for table in column_to_table_mapping[column]:
                        if table.lower() in tables:
                            table_column_key = f'{table}:{column}'
                            if table_column_key not in column_to_value:
                                column_to_value[table_column_key] = []

                            if operator == '=':
                                column_to_value[table_column_key].append(f'({value})')
                            elif operator == '!=':
                                column_to_value[table_column_key].append(f'(!={value})')

   
    for col in columns:  
        col = col.lower().strip()
        if col in column_to_table_mapping:
            for table in column_to_table_mapping[col]:
                if table.lower() in tables:
                    table_column_key = f'{table}:{col}'
                    if table_column_key not in column_to_value:
                        column_to_value[table_column_key] = []

    return column_to_value

def get_table_column_value(database_path, db_id, sql_schema, extracted_values):
    database_name = os.path.join(database_path, db_id + f"/{db_id}.sqlite")  
    table_column_mapping = get_column_table_mapping(database_name)

    formatted_result = map_columns_to_tables_and_values(sql_schema, extracted_values, table_column_mapping)
    return formatted_result
