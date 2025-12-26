instruction1 = (
    "Please generate SQL based on the given question and schema with no explanation. Pay attention to how the SQL structure matches the intent of the question.\n"
)
inputs1 = (
    "Question: {question}\n" \
    "Schema: {schema}\n" \
    "{keys}" \
    "For column names containing spaces, please strictly escape them as quotation marks.\n" \
    "SQL: ```sql```"
)

instruction2 = (
    "Please generate SQL based on the given question and schema with no explanation, ensuring the appropriate selection of schema in the SQL. The SQL logic can refer to the provided skeleton.\n"
)

inputs2 = (
    "Question: {question}\n" \
    "Schema: {schema}\n" \
    "{keys}" \
    "SQL Skeleton: {skeleton}" \
    "For column names containing spaces, please strictly escape them as quotation marks.\n" \
    "SQL: ```sql```"
)


instruction3 = (
    "The following SQL may contain errors or be correct. Please reanalyze the given question and generate the correct SQL without any explanation.\n"
)
inputs3 = (
    "Old SQL: {pred}\n" \
    "Question: {question}\n" \
    "Schema: {full_schema}\n" \
    "{keys}" \
    "For column names containing spaces, please strictly escape them as quotation marks.\n" \
    "SQL: ```sql```"
)