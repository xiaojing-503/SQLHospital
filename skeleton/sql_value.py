import re

def extract_column_and_value(conditions):  
    extracted_conditions = []  
    
    if not conditions:  
        return extracted_conditions  
    
    for condition in conditions:  
        if '=' in condition:  
            if '!=' in condition:  
                column, value = condition.split('!=', 1)  
            else:  
                column, value = condition.split('=', 1)  

            column = column.strip()  
            value = value.strip()  
            
            extracted_conditions.append((column, value))  
    
    return extracted_conditions  

def extract_values(pred_sql):
    pattern = r"(?:`([^`]+)`|\"([^\"]+)\"|(\w+))\s*(=|!=)\s*(?:'([^']*)'|\"([^\"]*)\")"
    matches = re.findall(pattern, pred_sql)

    results = []
    for match in matches:
        field_name = match[0] if match[0] else (match[1] if match[1] else match[2])  
        operator = match[3]  
        value = match[4] if match[4] else match[5]  

        results.append(f"{field_name} {operator} {value}")

    return results
