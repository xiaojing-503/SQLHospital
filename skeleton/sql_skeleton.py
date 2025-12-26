from sqlglot import parse_one, exp
import re

def get_sql_schema(sql):
    parsed_sql = parse_one(sql)
    tables = set()
    columns = set()
    values = set()
    for table in parsed_sql.find_all(exp.Table):
        tables.add(table.name)

    
    for column in parsed_sql.find_all(exp.Column):
        columns.add(column.alias_or_name)

    for literal in parsed_sql.find_all(exp.Literal):
        values.add(literal.this)

    return tables, columns, values

def remove_nested_functions(new_sql):
    while True:
        new_sql_temp = re.sub(r'\b(\w+)\(([^()]*?)\)', r'\1()', new_sql)
        
        if new_sql_temp == new_sql:
            break
            
        new_sql = new_sql_temp
        
    return new_sql

def replace_skeleton(sql, tables, columns, values):
    new_sql = sql

    for table in tables:
        new_sql = re.sub(rf'\b{re.escape(table)}\b', '_', new_sql)
    # print(new_sql)

    for column in columns:
        new_sql = re.sub(rf'\b{re.escape(column)}\b', '_', new_sql)
        new_sql = re.sub(rf"(?<!\w){re.escape(column)}(?!\w)", "_", new_sql, flags=re.IGNORECASE)

    # print(new_sql)

    for value in values:
        new_sql = re.sub(rf"(?<![Tt])\b{re.escape(str(value))}\b", "_", new_sql)
    # print(new_sql)

    # Remove values inside functions (e.g., IIF(time IS NOT NULL, 1, 0) -> IIF())
    new_sql = remove_nested_functions(new_sql)


    new_sql = re.sub(r'\"_\"', '_', new_sql)


    # print(new_sql)
    # table.column -> column (like _._ -> _)
    new_sql = re.sub(r'_\._', '_', new_sql, flags=re.IGNORECASE)
    new_sql = re.sub(r"_.'_'", '_', new_sql, flags=re.IGNORECASE)
    # print(new_sql)
    pattern = r'T\d?\._'  
    while re.search(pattern, new_sql, flags=re.IGNORECASE):  
        new_sql = re.sub(pattern, '_', new_sql, flags=re.IGNORECASE) 
    # print(new_sql)
    pattern2 = r'_,'
    while re.search(pattern2, new_sql, flags=re.IGNORECASE):  
        new_sql = re.sub(pattern2, '', new_sql, flags=re.IGNORECASE)  

    # Remove quotes around string literals
    new_sql = re.sub(r"'", '', new_sql)

    return new_sql

def get_sql_skeleton(sql):

    # sql = 'SELECT T2.driverRef, T2.nationality, T2.dob FROM qualifying AS T1 INNER JOIN drivers AS T2 on T1.driverId = T2.driverId WHERE T1.raceId = 23 AND T1.q2 IS NOT NULL'
    tables, columns, values = get_sql_schema(sql)
    # print(tables, columns, values)
    new_sql = replace_skeleton(sql, tables, columns, values)
    # print(new_sql)
    return new_sql
