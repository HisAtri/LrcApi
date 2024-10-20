from .db import sqlite

"""
{
    "table_name": "table_name",
    "type": ["json", "kv", "custom"],
    "fields": list[tuple[str, str]]
}
"""

def new(para: dict):
    table_name: str = para.get('table_name')
    table_type: str = para.get('type')
    if_not_exist: bool = para.get('if_not_exist', False)
    if not table_name:
        return None, "table_name is required"
    if not table_type:
        return None, "type is required"

    match table_type:
        case "custom":
            table_fields = para.get('fields')
            if not table_fields:
                return None, "fields is required"
            try:
                sqlite.create_table(table_name, table_fields, if_not_exist)
            except Exception as e:
                return None, str(e)
        case "json":
            try:
                sqlite.create_table(table_name, if_not_exist)
            except Exception as e:
                return None, str(e)

        case "kv":
            try:
                sqlite.init_kv_table(table_name)
            except Exception as e:
                return None, str(e)

        case _:
            return None, "type is invalid"
