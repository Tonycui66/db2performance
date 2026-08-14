"""
1. 生成的文件名 prepare_database.py
2. 负责：
   测试环境初始化
	create database
	create schema
	create table
	generate data
	cleanup

3. 输出统一的metrics
"""
import psycopg


def create_tables(conn):

    sql="""

    CREATE TABLE users(

    id BIGSERIAL PRIMARY KEY,

    name TEXT,

    created_at TIMESTAMP

    );

    """


    conn.execute(sql)
