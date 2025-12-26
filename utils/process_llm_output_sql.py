def format_sql_to_single_line(sql):  
    sql = sql.replace('```sql', '').strip() 
    sql = sql.replace('```\nsql', '').strip() 
    sql = sql.replace('```', '').strip()  
    sql = sql.replace('-- ', '').strip() 
     
    return ' '.join(line.strip() for line in sql.splitlines())  
