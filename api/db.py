from . import *

import re
from flask import request
from mod.auth import require_auth_decorator

from mod.db import SqliteDict

SQLITE_RESERVED_WORDS = {
    "ABORT", "ACTION", "ADD", "AFTER", "ALL", "ALTER", "ANALYZE", "AND", "AS", "ASC", "ATTACH", "AUTOINCREMENT",
    "BEFORE", "BEGIN", "BETWEEN", "BY", "CASCADE", "CASE", "CAST", "CHECK", "COLLATE", "COLUMN", "COMMIT",
    "CONFLICT", "CONSTRAINT", "CREATE", "CROSS", "CURRENT_DATE", "CURRENT_TIME", "CURRENT_TIMESTAMP", "DATABASE",
    "DEFAULT", "DEFERRABLE", "DEFERRED", "DELETE", "DESC", "DETACH", "DISTINCT", "DROP", "EACH", "ELSE", "END",
    "ESCAPE", "EXCEPT", "EXCLUSIVE", "EXISTS", "EXPLAIN", "FAIL", "FOR", "FOREIGN", "FROM", "FULL", "GLOB",
    "GROUP", "HAVING", "IF", "IGNORE", "IMMEDIATE", "IN", "INDEX", "INDEXED", "INITIALLY", "INNER", "INSERT",
    "INSTEAD", "INTERSECT", "INTO", "IS", "ISNULL", "JOIN", "KEY", "LEFT", "LIKE", "LIMIT", "MATCH", "NATURAL",
    "NO", "NOT", "NOTNULL", "NULL", "OF", "OFFSET", "ON", "OR", "ORDER", "OUTER", "PLAN", "PRAGMA", "PRIMARY",
    "QUERY", "RAISE", "RECURSIVE", "REFERENCES", "REGEXP", "REINDEX", "RELEASE", "RENAME", "REPLACE", "RESTRICT",
    "RIGHT", "ROLLBACK", "ROW", "SAVEPOINT", "SELECT", "SET", "TABLE", "TEMP", "TEMPORARY", "THEN", "TO", "TRANSACTION",
    "TRIGGER", "UNION", "UNIQUE", "UPDATE", "USING", "VACUUM", "VALUES", "VIEW", "VIRTUAL", "WHEN", "WHERE", "WITH",
    "WITHOUT"
}


def valide_tablename(table_name: str) -> tuple[bool, str, int]:
    if not table_name:
        return False, "Missing table_name.", 422
    invalid_chars = re.compile(r"[^a-zA-Z0-9_]")    # 表名仅允许包含字母、数字和下划线
    if invalid_chars.search(table_name):
        return False, "Invalid table_name: contains invalid characters.", 422
    if table_name.upper() in SQLITE_RESERVED_WORDS:
        return False, "Invalid table_name: is a reserved keyword.", 422
    # 限制表名长度为64字符
    if len(table_name) > 64:
        return False, "Invalid table_name: too long.", 422


def kv_set(table_name: str, para: dict) -> tuple[bool, str, int]:
    """
    写入或更新k-v数据
    """
    check_status: tuple[bool, str, int] = valide_tablename(table_name)
    if not check_status[0]:
        return check_status
    key = para.get("key")
    if not key:
        return False, "Missing key.", 422
    elif type(key) is not str:
        return False, "Invalid key: must be a string.", 422
    value = para.get("value")
    if not value:
        return False, "Missing value.", 422
    try:
        with SqliteDict(tablename=table_name) as db:
            db[key] = value
            db.commit()
    except Exception as e:
        return False, str(e), 500
    return True, table_name, 200

def kv_get(table_name: str, para: dict) -> tuple[bool, any, int]:
    """
    读取k-v数据
    """
    check_status: tuple[bool, str, int] = valide_tablename(table_name)
    if not check_status[0]:
        return check_status
    key = para.get("key")
    if not key:
        return False, "Missing key.", 422
    elif type(key) is not str:
        return False, "Invalid key: must be a string.", 422
    try:
        with SqliteDict(tablename=table_name) as db:
            return True, db[key], 200
    except KeyError:
        return False, "Key not found.", 404
    except Exception as e:
        return False, str(e), 500

def kv_del(table_name: str, para: dict) -> tuple[bool, any, int]:
    """
    删除k-v数据
    """
    check_status: tuple[bool, str, int] = valide_tablename(table_name)
    if not check_status[0]:
        return check_status
    key = para.get("key")
    if not key:
        return False, "Missing key.", 422
    elif type(key) is not str:
        return False, "Invalid key: must be a string.", 422

    try:
        with SqliteDict(tablename=table_name) as db:
            del db[key]
            db.commit()
            return True, key, 200
    except KeyError:
        return False, "Key not found.", 404
    except Exception as e:
        return False, str(e), 500

@v1_bp.route("/db/<path:table_name>", methods=["POST", "PUT", "GET", "DELETE"])
@require_auth_decorator(permission='rw')
def db_set(table_name):
    """
    写入或更新k-v数据
    """
    para: dict = request.json
    if not para:
        return {"code": 422, "message": "Missing JSON."}, 422

    type = para.get("type")
    if not type:
        return {"code": 422, "message": "Missing type."}, 422
    match type:
        case "kv":
            if request.method == "POST" or request.method == "PUT":
                status, message, code = kv_set(table_name, para)
                return {"code": code, "message": message}, code
            elif request.method == "GET":
                status, message, code = kv_get(table_name, para)
                if status:
                    return message, 200
                else:
                    return {"code": code, "message": message}, code
            elif request.method == "DELETE":
                status, message, code = kv_del(table_name, para)
                if status:
                    return message, 200
                else:
                    return {"code": code, "message": message}, code
        case _:
            return {"code": 422, "message": "Invalid type."}, 422

