import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"

import json

import numpy as np
import pandas as pd
import pydash
from datasets import concatenate_datasets, load_dataset
from peft import LoraConfig, TaskType, get_peft_model

with open("/path/spider/db_schemas.json") as f:
    db_schemas = json.load(f)


def update_type(col_type):
    if "char" in col_type or col_type == "" or "text" in col_type or "var" in col_type:
        return "text"
    elif (
        "int" in col_type
        or "numeric" in col_type
        or "decimal" in col_type
        or "number" in col_type
        or "id" in col_type
        or "real" in col_type
        or "double" in col_type
        or "float" in col_type
    ):
        return "number"
    elif "date" in col_type or "time" in col_type:
        return "date"
    elif "boolean" in col_type or col_type == "bit":
        return "boolean"
    else:
        return "others"


def create_table_prompt(
    sample, add_column_types=True, add_pk=True, add_fk=True
):
    db_id = sample["db_id"]
    tables = db_schemas[db_id]["tables"]
    pk = db_schemas[db_id].get("pk", None)
    fk = db_schemas[db_id].get("fk", None)


    formatted_columns = lambda table_name, columns: ",".join(
        [
            "{column_name}{column_type}".format(
                column_name=column[0],
                column_type=f" {update_type(column[1])}" if add_column_types else "",
            )
            for column in columns
        ]
    )

    formatted_table_pk = lambda table_pk: ",primary key ( {table_pk} )".format(
        table_pk=" , ".join(table_pk)
    )

    formatted_table_fk = lambda table_fk: ",{table_fk}".format(
        table_fk=",".join(
            [
                "foreign key ( {fk_columns_name} ) references {referenced_table_name} ( {referenced_columns_name} )".format(
                    fk_columns_name=" , ".join(
                        [fk_column[0] for fk_column in fk_columns]
                    ),
                    referenced_table_name=referenced_table_name,
                    referenced_columns_name=" , ".join(
                        [fk_column[1] for fk_column in fk_columns]
                    ),
                )
                for referenced_table_name, fk_columns in table_fk.items()
            ]
        )
    )

    prompt = "".join(
        [
            "{table_name}({formatted_columns}{formatted_table_pk}{formatted_table_fk}); ".format(
                table_name=table_name,
                formatted_columns=formatted_columns(table_name, columns),
                formatted_table_pk=formatted_table_pk(pk[table_name])
                if add_pk and pk and pydash.has(pk, table_name)
                else "",
                formatted_table_fk=formatted_table_fk(fk[table_name])
                if add_fk and fk and pydash.has(fk, table_name)
                else "",
            )
            for table_name, columns in tables.items()
        ]
    )

    return prompt


def create_prompt(sample):
    db_id = sample["db_id"]

    prompt = create_table_prompt(sample=sample, add_column_types=False, add_pk=False, add_fk=False)

    return prompt


