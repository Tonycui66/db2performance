from abc import ABC, abstractmethod
from typing import Dict, List, Any
from psycopg import Connection
from ..models import BenchmarkConfig


class DatabaseAdapter(ABC):
    \"\"\"
    Abstract base class for database adapters.
    All database implementations must extend this class.
    \"\"\"
    
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.connection: Connection = None
        
    @abstractmethod
    def connect(self) -> None:
        \"\"\"Establish connection to the database.\"\"\"
        pass
        
    @abstractmethod
    def disconnect(self) -> None:
        \"\"\"Close database connection.\"\"\"
        pass
        
    @abstractmethod
    def create_schema(self, schema_sql: str) -> None:
        \"\"\"Create database schema for benchmark.\"\"\"
        pass
        
    @abstractmethod
    def load_data(self, data_sql: str) -> None:
        \"\"\"Load test data into database.\"\"\"
        pass
        
    @abstractmethod
    def cleanup(self) -> None:
        \"\"\"Clean up test data and schema.\"\"\"
        pass
        
    @abstractmethod
    def execute(self, query: str, params: tuple = None) -> List[tuple]:
        \"\"\"Execute a query and return results.\"\"\"
        pass
        
    @abstractmethod
    def get_connection_info(self) -> Dict[str, Any]:
        \"\"\"Get database connection information.\"\"\"
        pass
        
    @abstractmethod
    def get_system_metrics(self) -> Dict[str, Any]:
        \"\"\"Get database-specific system metrics.\"\"\"
        pass
        
    def validate_connection(self) -> bool:
        \"\"\"Test database connectivity.\"\"\"
        try:
            self.connect()
            self.disconnect()
            return True
        except Exception:
            return False
