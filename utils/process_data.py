from process.process_sql import get_schema, Schema, get_sql
import json
import os
import re
import sqlite3


with open("/path/spider/db_schemas.json") as f:
    db_schemas = json.load(f)

def find_foreign_key_references(db_id):
    tables = db_schemas[db_id]["tables"]
    fk = db_schemas[db_id].get("fk", {})

    references = []

    for referencing_table, foreign_keys in fk.items():
        for referenced_table, columns in foreign_keys.items():
            for column_pair in columns:
                referencing_column = column_pair[0]
                referenced_column = column_pair[1]
                reference_str = f"[{referencing_table}.{referencing_column} References {referenced_table}.{referenced_column}]"
                references.append(reference_str)

    return references

def find_tables(column_name, data):
    # print(column_name)
    column_name_lower = column_name.lower()
    matching_tables = []
    # print("schema:",data)
    for table, columns in data.items():
        columns_lower = [col.lower() for col in columns]
        if column_name_lower in columns_lower:
            matching_tables.append(table)
    return matching_tables if matching_tables else None

def extract_table_column_info_easy(sql_query,err_desc):

    column_pattern = re.compile(r'no such column: ((\w+)\.)?(\w+)')
    match = column_pattern.search(err_desc)
    if match:
        table_alias = match.group(2)
        column_name = match.group(3)
        return table_alias, column_name
    return None, None

def extract_table_column_info(sql_query,err_desc):

    table_alias_pattern = re.compile(r'(\w+)\s+AS\s+(\w+)')
    column_pattern = re.compile(r'no such column: ((\w+)\.)?(\w+)')
    
    alias_to_table = {alias: table for table, alias in table_alias_pattern.findall(sql_query)}
    print(alias_to_table)
    
    match = column_pattern.search(err_desc)
    if match:
        table_alias = match.group(2)
        column_name = match.group(3)
        real_table_name = alias_to_table.get(table_alias, None)
        return real_table_name, column_name
    return None, None

def get_columns_for_table(db_path, table_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
    table_exists = cursor.fetchone()

    if not table_exists:
        conn.close()
        raise ValueError(f"Table '{table_name}' does not exist in the database.")

    # cursor.execute(f"PRAGMA table_info({table_name});")
    cursor.execute(f'PRAGMA table_info("{table_name}");')

    columns = [column[1] for column in cursor.fetchall()]

    conn.close()

    return columns

import re

def get_place(sql_query, column_name):
    
    join_pattern = re.compile(r'JOIN\s+\w+\s+AS\s+\w+\s+ON\s+.*?(\w+\.\w+\s*=\s*\w+\.\w+)', re.IGNORECASE | re.DOTALL)

    
    join_clauses = join_pattern.findall(sql_query)
    # print("join_clauses")
    # print(join_clauses)
    
    for clause in join_clauses:
        # print(clause)
        join_conditions=[]
        split_clause=clause.replace(" ", "").split("=")
        split_clause1=split_clause[0]
        split_clause2=split_clause[1]
        # join_conditions = clause[0]
        column1=split_clause1.split(".")
        join_conditions.append(column1[1])
        column2=split_clause2.split(".")
        join_conditions.append(column2[1])
        # print(join_conditions)
        if column_name in join_conditions:
            return "join on"
    
    if column_name in sql_query:
        return "other"
    
    return "not found"


def get_join_table(err_pred, column_name):
    join_pattern = re.compile(r'JOIN\s+(\w+)\s+AS\s+(\w+)\s+ON\s+(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)', re.IGNORECASE)
    alias_pattern = re.compile(r'(\w+)\s+AS\s+(\w+)', re.IGNORECASE)
    
    join_matches = join_pattern.findall(err_pred)
    
    alias_matches = alias_pattern.findall(err_pred)
    
    table_alias_map = {alias: table for table, alias in alias_matches}
    
    for match in join_matches:
        # print(match)
        table2, alias2, alias1, col1, alias3, col2 = match
        if col1 == column_name or col2 == column_name:
            table1 = table_alias_map.get(alias1)
            table2 = table_alias_map.get(alias3)
            return table1, table2,alias1,alias3
    
    return None, None, None, None


def parse_sql_columns(sql_query):
    select_pattern = re.compile(r'SELECT\s+(?:DISTINCT\s+)?((?:\s*\w+\.\w+|\s*\w+)(?:\s*,\s*(?:\w+\.\w+|\w+))*)\s+FROM', re.IGNORECASE | re.DOTALL)

    from_pattern = re.compile(r'FROM\s+([\w\.]+)(?:\s+AS\s+)?([\w]*)', re.IGNORECASE)
    join_pattern = re.compile(r'JOIN\s+([\w\.]+)(?:\s+AS\s+)?([\w]*)', re.IGNORECASE)
    subquery_pattern = re.compile(r'\((SELECT.+?)\)', re.IGNORECASE | re.DOTALL)

    subqueries = subquery_pattern.findall(sql_query)
    subquery_columns = {}
    for subquery in subqueries:
        subquery_columns.update(parse_sql_columns(subquery))

    select_match = select_pattern.search(sql_query)
    if not select_match:
        return {}


    columns = [col.strip() for col in select_match.group(1).split(',')]


    from_match = from_pattern.search(sql_query)
    if not from_match:
        return {}


    tables = {from_match.group(2).lower() or from_match.group(1).lower(): from_match.group(1).lower()}


    for join_match in join_pattern.finditer(sql_query):
        alias = join_match.group(2).lower() or join_match.group(1).lower()
        tables[alias] = join_match.group(1).lower()



    alias_to_table = {alias.lower(): table.lower() for alias, table in tables.items()}


    column_table_mapping = {}
    for column in columns:
        if ' AS ' in column.upper():
            column, alias = re.split(r'\s+AS\s+', column, flags=re.IGNORECASE)
        else:
            alias = column

        if '.' in column:
            table_alias, col_name = column.split('.', 1)
            table_name = alias_to_table.get(table_alias.lower(), table_alias)
            column_table_mapping[col_name] = table_name
        else:
            column_table_mapping[alias.strip()] = 'Unknown'


    column_table_mapping.update(subquery_columns)

    return column_table_mapping

def extract_join_pairs(sql_query):
    join_on_pattern = re.compile(r'JOIN\s+([\w\.]+)(?:\s+AS\s+)?([\w]*)\s+ON\s+([\w\.]+)\s*=\s*([\w\.]+)', re.IGNORECASE)

    join_pairs = []
    for join_match in join_on_pattern.finditer(sql_query):
        right_table = join_match.group(1)
        right_alias = join_match.group(2) if join_match.group(2) else right_table
        left_table_col = join_match.group(3)
        right_table_col = join_match.group(4)

        left_table_alias = left_table_col.split('.')[0]
        right_table_alias = right_table_col.split('.')[0]

        join_pairs.append((left_table_alias, right_table_alias))

    return join_pairs

def extract_table_aliases(sql_query, alias):
    join_pattern = re.compile(r'([\w\.]+)(?:\s+AS\s+)?([\w]*)', re.IGNORECASE)

    aliases = {}
    
    for join_match in join_pattern.finditer(sql_query):
        table_name = join_match.group(1)
        table_alias = join_match.group(2) if join_match.group(2) else table_name
        aliases[table_alias.lower()] = table_name

    return aliases.get(alias.lower(), None)

def check_foreign_key_relationship(db_id, table1, table2):
    foreign_keys = find_foreign_key_references(db_id)
    
    table1 = table1.lower()
    table2 = table2.lower()
    # print(table1,table2)
    for fk_pair in foreign_keys:
        # print(fk_pair)
        fk_pair = fk_pair.strip('[]')
        # print(fk_pair)
        left_table, left_column = fk_pair.replace(" ", "").split("References")[0].split('.')
        right_table, right_column = fk_pair.replace(" ", "").split("References")[1].split('.')
        
        left_table = left_table.lower()
        right_table = right_table.lower()
        # print(left_table,right_table)
        if (left_table == table1 and right_table == table2) or (left_table == table2 and right_table == table1):
            return True
    
    return False
def find_key(foreign_keys, t1, t2):
   
    for fk in foreign_keys:
        fk = fk.strip('[] ')
        parts = fk.split('References')
        if len(parts) != 2:
            continue
        
        table1_col1 = parts[0].strip().split('.')
        table2_col2 = parts[1].strip().split('.')
        
        if len(table1_col1) != 2 or len(table2_col2) != 2:
            continue
        
        table1, col1 = table1_col1
        table2, col2 = table2_col2
        
        if (table1 == t1 and table2 == t2) or (table1 == t2 and table2 == t1):
            return (f'{table1}.{col1}', f'{table2}.{col2}')
    
    return (None, None)

def get_num(err_pred, column_name):
   
    pattern = re.compile(re.escape(column_name), re.IGNORECASE)
    matches = pattern.findall(err_pred)
    return len(matches)

def get_foreign_keys(db_dir, db_id, table_name):
   
    db_path = os.path.join(db_dir, db_id, db_id + ".sqlite")
    # print(f"Database path: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute(f'PRAGMA foreign_key_list("{table_name}");')

    foreign_keys = cursor.fetchall()
    
    # print(f"Foreign keys for {table_name}: {foreign_keys}")
    
    conn.close()
    
    formatted_fks = []
    for fk in foreign_keys:
        formatted_fk = f"{table_name} ({fk[3]}) References {fk[2]} ({fk[4]})"
        formatted_fks.append(formatted_fk)
    
    return formatted_fks

def get_all_foreign_keys(db_dir, db_id):
    db_path = os.path.join(db_dir, db_id, db_id + ".sqlite")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
    
    all_foreign_keys = {}
    for table in tables:
        foreign_keys = get_foreign_keys(db_dir, db_id, table)
        if foreign_keys:
            all_foreign_keys[table] = foreign_keys
    
    conn.close()

    return all_foreign_keys

def get_related_foreign_keys(db_dir, db_id, main_table):
    all_fks = get_all_foreign_keys(db_dir, db_id)
    
    related_fks = {}
    for table, fks in all_fks.items():
        for fk in fks:
            if main_table.lower() in fk.lower():
                if table not in related_fks:
                    related_fks[table] = []
                related_fks[table].append(fk)
    
    all_fk = []
    for table, fks in related_fks.items():
        for fk in fks:
            all_fk.append(fk)
    
    return all_fk

def from_column_to_table(item,error_message,db_dir):
    
    db_id=item.get("db_id","")

    db = os.path.join(db_dir, db_id, db_id + ".sqlite")
    schema = Schema(get_schema(db))

    all_items = []
    # plan=item.get("plan","")
    err_pred=item.get("err_pred","")
    # error_message=item.get("err_desc","")
    foreign_keys=find_foreign_key_references(db_id)
    table_alias, column_name = extract_table_column_info(err_pred,error_message)
    print("table_alias, column_name : ",table_alias, column_name)
    if table_alias==None:
        table_alias2, column_name = extract_table_column_info_easy(err_pred,error_message)
        print("table_alias, column_name : ",table_alias2, column_name)
    tables=find_tables(column_name, schema.schema)
    tips=""
    if tables==None:
        str_set=["avg","average","max","min"]
        flag=0
        for s in str_set:
            # print("column_name:",column_name)
            if s in column_name.lower():
                flag=1
                func=s
                tips=f"### Column '{column_name}' doesn't in database schema, please use '{func}()' instead of '{column_name}'. Please note that only the columns with errors need to be modified, and do not modify other parts!\n"
        if flag==0:
            tips=f"### Column '{column_name}' doesn't in database schema, please choose a column with similar meanings.\n"
    else:
        
      
        place = get_place(err_pred,column_name)
        # print("place:",place)
       
        if place != "join on":
            
            column_num=get_num(err_pred,column_name)

            is_in=0
            #
            for table in tables:
                # print(table)
                # print(err_pred)
                # print(table.lower() in err_pred.lower())
               
                table_num=get_num(err_pred,table)
                # if table.lower() in err_pred.lower():
                if table.lower() in err_pred.lower() and table_num==column_num:
                    is_in = 1
                    if table_alias==None:
                       
                        tips=f"### The column '{column_name}' in '{table_alias2}' is not selected.\n"
                    else:
                        tips=f"### The column '{column_name}' doesn't in table '{table_alias}' but in '{tables}', please select the correct table name mapping.\n"
            if is_in==0:
                if (len(tables)==1):
                    foreign_key=get_related_foreign_keys(db_dir, db_id, tables[0])
                    tips=f"### The column '{column_name}' in table '{tables}', with foreign key {foreign_key}.\n"
                else:
                    for table in tables:
                        foreign_key=get_related_foreign_keys(db_dir, db_id, table)
                        tips+=f"### The column '{column_name}' may in table '{table}', with foreign key {foreign_key}.\n"
                    tips+="### Please select the most suitable table to add to SQL query.\n"
        else:
            t1,t2,alias1,alias2=get_join_table(err_pred,column_name)
            # print(f"Table 1: {t1}, Table 2: {t2}")
            if t1!=None and t2!=None:
                
                has_fk = check_foreign_key_relationship(db_id, t1, t2)
                # 3
                if has_fk:
                    foreign_keys=find_foreign_key_references(db_id)
                    foreign_key1,foreign_key2=find_key(foreign_keys,t1,t2)
                    # print("foreign_key1,foreign_key2")
                    # print(foreign_key1,foreign_key2)
                    tips=f"### Foreign Key: {foreign_key1} = {foreign_key2}. Note: '{t1}' alias '{alias1}', '{t2}' alias '{alias2}' \n"
                else:
                    # tips=f"### There is no foreign key relationship defined between the '{t1}' table and the '{t2}' table. Please select a table with foreign key connections or add a third table. Note that you are unable to modify the database structure!\n"
                    join_1=get_foreign_keys(db_dir, db_id,t1)
                    join_2=get_foreign_keys(db_dir, db_id,t2)

                    tips=f"### There is no foreign key relationship defined between the '{t1}' table and the '{t2}' table.\n"
                    tips+=f"### Please select the most suitable table from the database to replace table '{table_alias}'. Candidate foreign keys in database schema: {join_1}\n"
                    tips+="### If a suitable table cannot be found for replacement, you can choose to add a third table with foreign key links to both tables. Please use this operation with caution.\n"
                    tips+="### You cannot create a new table or create a foreign key!!\n"
            else:
                tips=""
    return tips       


def extract_table_info(sql_query,err_desc):

    table_pattern = re.compile(r'no such table: (\w+)')
    
    match = table_pattern.search(err_desc)
    if match:
        table_name = match.group(1)
        return table_name
    return None

def get_all_table_names(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    
    tables = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    table_names = [table[0] for table in tables]
    
    return table_names

def no_such_table(item,error_message,db_dir):
    db_id=item.get("db_id","")

    db = os.path.join(db_dir, db_id, db_id + ".sqlite")

    err_pred=item.get("err_pred","")
    err_table=extract_table_info(err_pred,error_message)
    # print(err_table)
    tables=get_all_table_names(db)
    # print(tables)
    tips=f"### Table '{err_table}' does not exist in the database. Please either remove this table if not necessary, or select the correct table name from {tables}, with a detailed explanation.\n"
    
    
    tips+="### Note that only the incorrect table needs to be modified, and no other parts of the SQL need to be modified!"
    return tips

