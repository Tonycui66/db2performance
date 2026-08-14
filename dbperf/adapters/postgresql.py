from typing import Dict, List, Any, Tuple
import psycopg
from psycopg import sql, Error
from .base import DatabaseAdapter
from ..models import DatabaseMetrics


class PostgreSQLAdapter(DatabaseAdapter):
    \"\"\"
    PostgreSQL implementation of DatabaseAdapter.
    \"\"\"
    
    def __init__(self, dsn: str):
        super().__init__(dsn)
        
    def connect(self) -> None:
        \"\"\"Establish connection to PostgreSQL database.\"\"\"
        try:
            self.connection = psycopg.connect(self.dsn)
            print(f\"Connected to PostgreSQL: {self.get_connection_info()}\")
        except Error as e:
            raise ConnectionError(f\"Failed to connect to PostgreSQL: {e}\")
    
    def disconnect(self) -> None:
        \"\"\"Close PostgreSQL connection.\"\"\"
        if self.connection:
            self.connection.close()
            self.connection = None
            print(\"Disconnected from PostgreSQL\")
    
    def create_schema(self, schema_sql: str) -> None:
        \"\"\"Create database schema for benchmark.\"\"\"
        if not self.connection:
            self.connect()
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(schema_sql)
                self.connection.commit()
            print(\"Schema created successfully\")
        except Error as e:
            self.connection.rollback()
            raise RuntimeError(f\"Failed to create schema: {e}\")
    
    def load_data(self, data_sql: str) -> None:
        \"\"\"Load test data into PostgreSQL database.\"\"\"
        if not self.connection:
            self.connect()
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(data_sql)
                self.connection.commit()
            print(\"Data loaded successfully\")
        except Error as e:
            self.connection.rollback()
            raise RuntimeError(f\"Failed to load data: {e}\")
    
    def cleanup(self) -> None:
        \"\"\"Clean up test data and schema in PostgreSQL.\"\"\"
        if not self.connection:
            self.connect()
        
        cleanup_queries = [
            \"DROP TABLE IF EXISTS users\",
            \"DROP TABLE IF EXISTS orders\",
            \"DROP TABLE IF EXISTS products\",
            \"DROP EXTENSION IF EXISTS pg_stat_statements\"
        ]
        
        try:
            with self.connection.cursor() as cursor:
                for query in cleanup_queries:
                    cursor.execute(query)
                self.connection.commit()
            print(\"Cleanup completed successfully\")
        except Error as e:
            self.connection.rollback()
            raise RuntimeError(f\"Failed to cleanup: {e}\")
    
    def execute(self, query: str, params: Tuple = None) -> List[Tuple]:
        \"\"\"Execute a query and return results.\"\"\"
        if not self.connection:
            self.connect()
        
        try:
            with self.connection.cursor() as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                return cursor.fetchall()
        except Error as e:
            raise RuntimeError(f\"Query execution failed: {e}\")
    
    def get_connection_info(self) -> Dict[str, Any]:
        \"\"\"Get PostgreSQL connection information.\"\"\"
        if not self.connection:
            return {}
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(\"SELECT version(), current_database(), current_user\")
                result = cursor.fetchone()
                return {
                    \"version\": result[0] if result else \"Unknown\",
                    \"database\": result[1] if result else \"Unknown\",
                    \"user\": result[2] if result else \"Unknown\"
                }
        except Error:
            return {}
    
    def get_system_metrics(self) -> DatabaseMetrics:
        \"\"\"Get PostgreSQL-specific system metrics.\"\"\"
        if not self.connection:
            self.connect()
        
        try:
            # Get connection count
            connection_query = \"SELECT COUNT(*) FROM pg_stat_activity WHERE state = 'active'\"
            active_connections = self.execute(connection_query)[0][0]
            
            # Get transaction metrics
            transaction_query = \"\"\"SELECT 
                sum(xact_commit) as commits,
                sum(xact_rollback) as rollbacks
                FROM pg_stat_database\"\"\"
            transaction_result = self.execute(transaction_query)[0]
            
            # Get cache metrics
            cache_query = \"\"\"SELECT 
                sum(blks_hit) as hits,
                sum(blks_read) as reads
                FROM pg_stat_database\"\"\"
            cache_result = self.execute(cache_query)[0]
            cache_hit_ratio = cache_result[0] / (cache_result[0] + cache_result[1]) if (cache_result[0] + cache_result[1]) > 0 else 0
            
            # Get WAL metrics
            wal_query = \"SELECT pg_current_wal_lsn() - pg_current_wal_insert_lsn() as wal_bytes\"
            wal_bytes = self.execute(wal_query)[0][0]
            
            # Get lock metrics
            lock_query = \"SELECT COUNT(*) FROM pg_locks WHERE granted = true\"
            lock_count = self.execute(lock_query)[0][0]
            
            return DatabaseMetrics(
                connection_count=active_connections,
                transaction_commit_total=transaction_result[0],
                transaction_rollback_total=transaction_result[1],
                cache_hit_ratio=cache_hit_ratio,
                wal_bytes=int(wal_bytes),
                wal_records=0,  # Would need additional query
                lock_count=lock_count,
                slow_query_count=0  # Would need pg_stat_statements
            )
        except Error as e:
            print(f\"Warning: Failed to get PostgreSQL metrics: {e}\")
            return DatabaseMetrics(0, 0, 0, 0, 0, 0, 0, 0)
