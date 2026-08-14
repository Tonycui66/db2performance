"""
1. 生成的文件名 collect_postgres_metrics.py
2. 数据库内部
	Connection
	Transaction
	Cache
	WAL
	Checkpoint
	Locks
	Vacuum
	Slow SQL
3. 输出统一的metrics
"""
import psycopg


class PostgreSQLCollector:


    def __init__(self,dsn):

        self.conn=psycopg.connect(dsn)



    def query(self,sql):

        with self.conn.cursor() as cur:

            cur.execute(sql)

            return cur.fetchall()



    def collect_connections(self):

        sql="""

        SELECT count(*)

        FROM pg_stat_activity

        """

        return self.query(sql)



    def collect_cache_hit(self):

        sql="""

        SELECT

        sum(blks_hit)/
        (
        sum(blks_hit)+sum(blks_read)
        )

        FROM pg_stat_database

        """

        return self.query(sql)


