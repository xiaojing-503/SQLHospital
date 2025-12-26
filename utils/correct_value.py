import sqlite3
import sqlite3

def find_similar_values_in_all_tables(db_path, value, case_sensitive=False):
   
    value_length = len(value) * 2
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    similar_values = []

    like_operator = "COLLATE NOCASE" if not case_sensitive else ""

    for table_tuple in tables:
        table_name = table_tuple[0]

        cursor.execute(f"PRAGMA table_info(`{table_name}`);")
        columns = cursor.fetchall()

        for column in columns:
            column_name_in_table = column[1]

            like_query = f"""
                SELECT DISTINCT `{column_name_in_table}` 
                FROM `{table_name}` 
                WHERE `{column_name_in_table}` LIKE ?
                {like_operator}
            """

            cursor.execute(like_query, ('%' + value + '%',))
            db_values = cursor.fetchall()

            for db_value_tuple in db_values:
                db_value = db_value_tuple[0]

                if db_value is not None and len(str(db_value)) <= value_length:
                    similar_values.append((table_name, column_name_in_table, str(db_value)))  

    conn.close()

    return similar_values
