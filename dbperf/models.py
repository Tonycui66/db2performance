"
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field


class MetricType(str, Enum):
    GAUGE = \
gauge\
    COUNTER = \counter\
    HISTOGRAM = \histogram\


class MetricSource(str, Enum):
    SYSTEM = \system\
    DATABASE = \database\
    WORKLOAD = \workload\


@dataclass
class Metric:
    timestamp: float
    metric_name: str
    metric_type: MetricType
    value: Union[float, int]
    unit: str
    source: MetricSource
    tags: Dict[str, str] = Field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            \timestamp\: self.timestamp,
            \metric_name\: self.metric_name,
            \metric_type\: self.metric_type.value,
            \value\: self.value,
            \unit\: self.unit,
            \source\: self.source.value,
            \tags\: self.tags
        }


@dataclass
class SystemMetrics:
    cpu_usage: float
    memory_usage: float
    disk_read_bytes: int
    disk_write_bytes: int
    network_bytes_sent: int
    network_bytes_recv: int
    load_average: float


@dataclass
class DatabaseMetrics:
    connection_count: int
    transaction_commit_total: int
    transaction_rollback_total: int
    cache_hit_ratio: float
    wal_bytes: int
    wal_records: int
    lock_count: int
    slow_query_count: int


@dataclass
class WorkloadMetrics:
    tps: float
    qps: float
    latency_p50: float
    latency_p95: float
    latency_p99: float
    error_rate: float


@dataclass
class BenchmarkResult:
    benchmark_id: str
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    system_metrics: SystemMetrics
    database_metrics: DatabaseMetrics
    workload_metrics: WorkloadMetrics
    summary: Dict[str, Any]
    bottlenecks: List[str]
    recommendations: List[str]


@dataclass
class BenchmarkConfig:
    name: str
    description: str
    database_dsn: str
    workload_type: str
    duration_minutes: int
    warmup_minutes: int
    concurrent_users: int
    query_mix: Dict[str, float]
    target_database: str = \postgresql\
    
    def validate(self) -> bool:
        required_fields = [\name\, \database_dsn\, \workload_type\]
        return all(getattr(self, field) for field in required_fields)


@dataclass
class WorkloadConfig:
    name: str
    query_templates: List[str]
    think_time_ms: int
    iterations: int
    validation_rules: List[str]


class BenchmarkStatus(str, Enum):
    PENDING = \pending\
    WARMUP = \warmup\
    MEASUREMENT = \measurement\
    ANALYSIS = \analysis\
    COMPLETED = \completed\
    FAILED = \failed\
"
