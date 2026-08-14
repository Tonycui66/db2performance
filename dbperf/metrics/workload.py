import time
import threading
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from ..models import Metric, MetricType, MetricSource, WorkloadMetrics


@dataclass
class QueryLatency:
    query: str
    start_time: float
    end_time: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None


class WorkloadMetricsCollector:
    \"\"\"
    Collects workload-specific metrics during benchmark execution.
    \"\"\"
    
    def __init__(self):
        self.query_latencies: List[QueryLatency] = []
        self.start_time: Optional[float] = None
        self.success_count = 0
        self.error_count = 0
        self.lock = threading.Lock()
    
    def start_collection(self) -> None:
        \"\"\"Start collecting workload metrics.\"\"\"
        self.start_time = time.time()
        self.query_latencies = []
        self.success_count = 0
        self.error_count = 0
    
    def record_query(self, query: str, start_time: float, end_time: float, success: bool = True, error_message: Optional[str] = None) -> None:
        \"\"\"Record a query execution.\"\"\"
        with self.lock:
            latency = QueryLatency(query, start_time, end_time, success, error_message)
            self.query_latencies.append(latency)
            
            if success:
                self.success_count += 1
            else:
                self.error_count += 1
    
    def get_current_metrics(self) -> WorkloadMetrics:
        \"\"\"Calculate current workload metrics.\"\"\"
        if not self.start_time:
            return WorkloadMetrics(0, 0, 0, 0, 0, 0)
        
        current_time = time.time()
        duration = current_time - self.start_time
        total_queries = len(self.query_latencies)
        
        if total_queries == 0:
            return WorkloadMetrics(0, 0, 0, 0, 0, 0)
        
        # Calculate latencies
        latencies = []
        for query in self.query_latencies:
            if query.end_time and query.start_time:
                latencies.append(query.end_time - query.start_time)
        
        if not latencies:
            return WorkloadMetrics(0, 0, 0, 0, 0, 0)
        
        # Calculate percentiles
        sorted_latencies = sorted(latencies)
        p50 = self._percentile(sorted_latencies, 50)
        p95 = self._percentile(sorted_latencies, 95)
        p99 = self._percentile(sorted_latencies, 99)
        
        # Calculate rates
        tps = total_queries / duration if duration > 0 else 0
        qps = total_queries / duration if duration > 0 else 0
        error_rate = (self.error_count / total_queries) if total_queries > 0 else 0
        
        return WorkloadMetrics(
            tps=tps,
            qps=qps,
            latency_p50=p50,
            latency_p95=p95,
            latency_p99=p99,
            error_rate=error_rate
        )
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        \"\"\"Calculate percentile of a list of values.\"\"\"
        if not data:
            return 0.0
        
        index = (percentile / 100) * (len(data) - 1)
        if index.is_integer():
            return data[int(index)]
        else:
            lower = data[int(index)]
            upper = data[int(index) + 1]
            weight = index - int(index)
            return lower + (upper - lower) * weight
    
    def collect_metrics(self) -> Dict[str, Any]:
        \"\"\"Collect workload metrics in JSONL-compatible format.\"\"\"
        metrics = {}
        current_metrics = self.get_current_metrics()
        
        metrics[\"workload.tps\"] = {
            \"value\": current_metrics.tps,
            \"unit\": \"transactions/sec\",
            \"type\": \"gauge\"
        }
        
        metrics[\"workload.qps\"] = {
            \"value\": current_metrics.qps,
            \"unit\": \"queries/sec\",
            \"type\": \"gauge\"
        }
        
        metrics[\"workload.latency.p50\"] = {
            \"value\": current_metrics.latency_p50,
            \"unit\": \"seconds\",
            \"type\": \"gauge\"
        }
        
        metrics[\"workload.latency.p95\"] = {
            \"value\": current_metrics.latency_p95,
            \"unit\": \"seconds\",
            \"type\": \"gauge\"
        }
        
        metrics[\"workload.latency.p99\"] = {
            \"value\": current_metrics.latency_p99,
            \"unit\": \"seconds\",
            \"type\": \"gauge\"
        }
        
        metrics[\"workload.error_rate\"] = {
            \"value\": current_metrics.error_rate,
            \"unit\": \"percent\",
            \"type\": \"gauge\"
        }
        
        return metrics
    
    def create_metric_objects(self) -> List[Metric]:
        \"\"\"Convert collected metrics to Metric objects.\"\"\"
        metrics_data = self.collect_metrics()
        timestamp = time.time()
        metric_objects = []
        
        for name, data in metrics_data.items():
            metric = Metric(
                timestamp=timestamp,
                metric_name=name,
                metric_type=MetricType(data[\"type\"]),
                value=data[\"value\"],
                unit=data[\"unit\"],
                source=MetricSource.WORKLOAD,
                tags={}
            )
            metric_objects.append(metric)
        
        return metric_objects
    
    def get_query_summary(self) -> Dict[str, Any]:
        \"\"\"Get a summary of query executions.\"\"\"
        if not self.query_latencies:
            return {}
        
        total_duration = sum(q.end_time - q.start_time if q.end_time and q.start_time else 0 for q in self.query_latencies)
        avg_latency = total_duration / len(self.query_latencies) if self.query_latencies else 0
        
        return {
            \"total_queries\": len(self.query_latencies),
            \"successful_queries\": self.success_count,
            \"failed_queries\": self.error_count,
            \"average_latency\": avg_latency,
            \"min_latency\": min(q.end_time - q.start_time if q.end_time and q.start_time else float('inf') for q in self.query_latencies),
            \"max_latency\": max(q.end_time - q.start_time if q.end_time and q.start_time else 0 for q in self.query_latencies)
        }
