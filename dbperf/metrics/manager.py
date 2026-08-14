import time
import json
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime
from .system import SystemMetricsCollector
from .database import DatabaseMetricsCollector
from .workload import WorkloadMetricsCollector
from ..models import Metric, MetricSource
from ..adapters.base import DatabaseAdapter


class MetricsManager:
    \"\"\"
    Central metrics collection and management system.
    Coordinates between system, database, and workload metrics.
    \"\"\"
    
    def __init__(self, adapter: Optional[DatabaseAdapter] = None):
        self.system_collector = SystemMetricsCollector()
        self.database_collector = DatabaseMetricsCollector(adapter) if adapter else None
        self.workload_collector = WorkloadMetricsCollector()
        self.is_collecting = False
        self.collection_thread = None
        self.output_file = None
        self.lock = threading.Lock()
    
    def start_collection(self, output_file: str = \"metrics.jsonl\") -> None:
        \"\"\"Start continuous metrics collection.\"\"\"
        self.output_file = output_file
        self.is_collecting = True
        self.workload_collector.start_collection()
        
        # Start collection thread
        self.collection_thread = threading.Thread(target=self._collection_loop, daemon=True)
        self.collection_thread.start()
        
        print(f\"Started metrics collection to {output_file}\")
    
    def stop_collection(self) -> None:
        \"\"\"Stop metrics collection.\"\"\"
        self.is_collecting = False
        if self.collection_thread:
            self.collection_thread.join(timeout=5)
        
        if self.output_file:
            print(f\"Stopped metrics collection. Data saved to {self.output_file}\")
    
    def _collection_loop(self) -> None:
        \"\"\"Main collection loop running in background thread.\"\"\"
        while self.is_collecting:
            timestamp = time.time()
            metrics_batch = []
            
            # Collect system metrics
            try:
                system_metrics = self.system_collector.create_metric_objects()
                metrics_batch.extend(system_metrics)
            except Exception as e:
                print(f\"Error collecting system metrics: {e}\")
            
            # Collect database metrics (if adapter available)
            if self.database_collector:
                try:
                    db_metrics = self.database_collector.create_metric_objects()
                    metrics_batch.extend(db_metrics)
                except Exception as e:
                    print(f\"Error collecting database metrics: {e}\")
            
            # Collect workload metrics
            try:
                workload_metrics = self.workload_collector.create_metric_objects()
                metrics_batch.extend(workload_metrics)
            except Exception as e:
                print(f\"Error collecting workload metrics: {e}\")
            
            # Write to file
            self._write_metrics(metrics_batch)
            
            # Sleep for 1 second
            time.sleep(1)
    
    def _write_metrics(self, metrics: List[Metric]) -> None:
        \"\"\"Write metrics to JSONL file.\"\"\"
        with self.lock:
            if not self.output_file:
                return
            
            try:
                with open(self.output_file, 'a') as f:
                    for metric in metrics:
                        json_line = json.dumps(metric.to_dict())
                        f.write(json_line + '\n')
            except Exception as e:
                print(f\"Error writing metrics to file: {e}\")
    
    def record_query(self, query: str, start_time: float, end_time: float, success: bool = True, error_message: Optional[str] = None) -> None:
        \"\"\"Record a query execution for workload metrics.\"\"\"
        self.workload_collector.record_query(query, start_time, end_time, success, error_message)
    
    def get_current_workload_metrics(self) -> Dict[str, Any]:
        \"\"\"Get current workload metrics.\"\"\"
        return self.workload_collector.get_current_metrics().__dict__
    
    def get_workload_summary(self) -> Dict[str, Any]:
        \"\"\"Get workload execution summary.\"\"\"
        return self.workload_collector.get_query_summary()
    
    def collect_on_demand(self) -> List[Metric]:
        \"\"\"Collect metrics on demand (without background thread).\"\"\"
        metrics = []
        
        try:
            system_metrics = self.system_collector.create_metric_objects()
            metrics.extend(system_metrics)
        except Exception as e:
            print(f\"Error collecting system metrics: {e}\")
        
        if self.database_collector:
            try:
                db_metrics = self.database_collector.create_metric_objects()
                metrics.extend(db_metrics)
            except Exception as e:
                print(f\"Error collecting database metrics: {e}\")
        
        try:
            workload_metrics = self.workload_collector.create_metric_objects()
            metrics.extend(workload_metrics)
        except Exception as e:
            print(f\"Error collecting workload metrics: {e}\")
        
        return metrics
