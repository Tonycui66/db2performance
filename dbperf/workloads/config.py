from dataclasses import dataclass
from typing import Dict, List, Any
from enum import Enum


class WorkloadType(str, Enum):
    OLTP = "oltp"
    OLAP = "olap"
    MIXED = "mixed"


class QueryType(str, Enum):
    SELECT = "select"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"


@dataclass
class QueryTemplate:
    query_type: QueryType
    template: str
    weight: float
    validation_rules: List[str] = None
    
    def validate_result(self, result: List[tuple]) -> bool:
        \"\"\"Validate query result based on rules.\"\"\"
        if not self.validation_rules:
            return True
        
        for rule in self.validation_rules:
            if rule == \"non_empty\" and not result:
                return False
            elif rule == \"single_row\" and len(result) != 1:
                return False
            elif rule == \"multiple_rows\" and len(result) < 2:
                return False
        
        return True


@dataclass
class WorkloadConfig:
    name: str
    workload_type: WorkloadType
    query_templates: List[QueryTemplate]
    think_time_ms: int = 0
    iterations: int = 1
    concurrent_users: int = 1
    warmup_iterations: int = 0
    
    def normalize_weights(self) -> None:
        \"\"\"Normalize query weights to sum to 1.0.\"\"\"
        total_weight = sum(qt.weight for qt in self.query_templates)
        if total_weight > 0:
            for qt in self.query_templates:
                qt.weight = qt.weight / total_weight
    
    def validate(self) -> bool:
        \"\"\"Validate workload configuration.\"\"\"
        if not self.query_templates:
            return False
        
        if self.concurrent_users < 1:
            return False
        
        if self.think_time_ms < 0:
            return False
        
        if sum(qt.weight for qt in self.query_templates) == 0:
            return False
        
        return True
