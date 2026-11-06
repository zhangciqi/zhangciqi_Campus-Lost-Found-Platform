# backend/database.py
import pymysql

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "root123",          # 本地数据库密码，与 Navicat 连接配置一致
    "database": "campus_lost_found",
    "charset": "utf8mb4"
}

def get_conn():
    return pymysql.connect(**DB_CONFIG)
