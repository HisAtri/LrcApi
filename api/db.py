from . import *

import re
import sqlite3
from datetime import datetime, timezone
from flask import request, jsonify
from mod.auth import require_auth_decorator

from mod.db import SqliteDict, saved_path


def validate_table_name(table_name: str) -> tuple[bool, str, int]:
    if not table_name:
        return False, "Missing table_name.", 422
    invalid_chars = re.compile(r"[^a-zA-Z0-9_]")  # 表名仅允许包含字母、数字和下划线
    if invalid_chars.search(table_name):
        return False, "Invalid table_name: contains invalid characters.", 422
    # 限制表名长度为64字符
    if len(table_name) > 64:
        return False, "Invalid table_name: too long.", 422
    return True, "OK", 200


def kv_set(table_name: str, para: dict) -> tuple[bool, str|dict, int]:
    """
    写入或更新k-v数据
    """
    check_status: tuple[bool, str, int] = validate_table_name(table_name)
    if not check_status[0]:
        return check_status
    kv_list: dict[str, str] = para.get("data")
    results: dict = {}
    with SqliteDict(tablename=table_name) as db:
        for key, value in kv_list.items():
            try:
                db[key] = value
                db.commit()
                results[key] = {
                    "status": "Success",
                    "timezone": int(datetime.now(timezone.utc).timestamp()),
                }
            except Exception as e:
                results[key] = {
                    "status": "Error",
                    "Message": str(e),
                    "timezone": int(datetime.now(timezone.utc).timestamp()),
                }
    return True, results, 200


def kv_get(table_name: str, para: dict) -> tuple[bool, any, int]:
    """
    读取k-v数据
    """
    results: dict = {}
    check_status: tuple[bool, str, int] = validate_table_name(table_name)
    if not check_status[0]:
        return check_status
    keys = para.get("keys")
    if not keys:
        return False, "Missing key.", 422
    elif type(keys) is not list:
        return False, "Invalid key: must be a list.", 422
    with SqliteDict(tablename=table_name) as db:
        for key in keys:
            results[key] = db.get(key, None)
    return True, results, 200


def kv_del(table_name: str, para: dict) -> tuple[bool, any, int]:
    """
    删除k-v数据
    """
    results: dict = {}
    check_status: tuple[bool, str, int] = validate_table_name(table_name)
    if not check_status[0]:
        return check_status
    keys = para.get("keys")
    if not keys:
        return False, "Missing keys.", 422
    elif type(keys) is not list:
        return False, "Invalid keys: must be a list.", 422

    with SqliteDict(tablename=table_name) as db:
        for key in keys:
            try:
                del db[key]
                db.commit()
                results[key] = {
                    "status": "Success",
                    "timezone": int(datetime.now(timezone.utc).timestamp()),
                }
            except KeyError:
                results[key] = {
                    "status": "Error",
                    "Message": "Key not found",
                    "timezone": int(datetime.now(timezone.utc).timestamp()),
                }
            except Exception as e:
                results[key] = {
                    "status": "Error",
                    "Message": str(e),
                    "timezone": int(datetime.now(timezone.utc).timestamp()),
                }


def custom_sql(sql: str) -> list[dict]:
    with sqlite3.connect(saved_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql)
        rows: list = cursor.fetchall()
        return [dict(row) for row in rows]


@v1_bp.route("/db/<path:table_name>", methods=["POST", "PUT", "GET", "DELETE"], endpoint='db_set_endpoint')
@require_auth_decorator(permission='rw')
def db_set(table_name):
    """
    写入或更新k-v数据
    Elastic API都能往GET请求体里塞东西，我为什么不行
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


@v1_bp.route("/db", methods=["POST"], endpoint='db_custom')
@require_auth_decorator(permission='rw')
def db_custom():
    """
    执行自定义的SQL
    返回json结果
    此操作敏感，因此必须有可信授权
    用户必须保证使用者受到信任
    """
    para: dict = request.json
    if not para or not (sql := para.get('sql')):
        logger.warning("The request submitted by the client lacks necessary parameters")
        return jsonify({
            "status": "Error",
            "code": 400,
            "timezone": int(datetime.now(timezone.utc).timestamp()),
            "message": "Missing 'sql' parameter"
        }), 400

    results = []
    for s in sql:
        try:
            result: list[dict] = custom_sql(sql=s)
            results.append({
                "sql": s,
                "status": "Success",
                "code": 200,
                "timezone": int(datetime.now(timezone.utc).timestamp()),
                "result": result
            })
        except sqlite3.Error as e:
            logger.error(f"SQLite error during custom SQL execution: {str(e)}")
            results.append({
                "sql": s,
                "status": "Error",
                "code": 500,
                "timezone": int(datetime.now(timezone.utc).timestamp()),
                "message": f"SQLite error: {str(e)}"
            })
        except Exception as e:
            logger.error(f"Server error during custom SQL execution: {str(e)}")
            results.append({
                "sql": s,
                "status": "Error",
                "code": 500,
                "timezone": int(datetime.now(timezone.utc).timestamp()),
                "message": f"Server error: {str(e)}"
            })

    return jsonify(results)
