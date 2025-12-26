def format_database_schema(data_dict):
    tables = {}

    for key in data_dict.keys():
        table, column = key.split(':')
        if table not in tables:
            tables[table] = []
        if column not in tables[table]:
            tables[table].append(column)

    result_lines = []

    for table, columns in tables.items():
        formatted_columns = []

        for column in columns:
            full_column_name = f"{table}:{column}"
            values = data_dict[full_column_name]

            if values:  
                formatted_values = []
                for value in values:
                    if value.startswith('(') and value.endswith(')'): 
                        formatted_values.append(f"{value[1:-1]}")  
                    else:
                        formatted_values.append(value)

                
                formatted_values_str = ', '.join(formatted_values)

                
                formatted_column = f"`{column}` (values: '{formatted_values_str}')"
            else:  
                formatted_column = f"`{column}`"

            formatted_columns.append(formatted_column)

        result_lines.append(f"table {table.lower()}, columns = [{', '.join(formatted_columns)}]")

    return '; '.join(result_lines)
