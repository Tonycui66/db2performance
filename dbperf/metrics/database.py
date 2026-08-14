import time
from typing import Dict, Any, List
from ..models import Metric, MetricType, MetricSource, DatabaseMetrics
from ..adapters.base import DatabaseAdapter


class DatabaseMetricsCollector:
    \"\"\"
    Collects database-specific metrics from PostgreSQL adapter.
    \"\"\"
    
    def __init__(self, adapter: DatabaseAdapter):
        self.adapter = adapter
        self.last_metrics = None
    
    def collect_current_metrics(self) -> DatabaseMetrics:
        \"\"\"Collect current database metrics.\"\"\"
        return self.adapter.get_system_metrics()
    
    def collect_metrics(self) -> Dict[str, Any]:
        \"\"\"Collect database metrics in JSONL-compatible format.\"\"\"
        metrics = {}
        db_info = self.adapter.get_connection_info()
        
        try:
            # Connection metrics
            active_connections_query = \"SELECT COUNT(*) FROM pg_stat_activity WHERE state = 'active'\"
            active_connections = self.adapter.execute(active_connections_query)[0][0]
            metrics[\"db.connection.active\"] = {
                \"value\": active_connections,
                \"unit\": \"\",
                \"type\": \"gauge\"
            }
            
            # Transaction metrics
            transaction_query = \"\"\"SELECT 
                sum(xact_commit) as commits,
                sum(xact_rollback) as rollbacks
                FROM pg_stat_database\"\"\"
            transaction_result = self.adapter.execute(transaction_query)[0]
            
            metrics[\"db.transaction.commit_total\"] = {
                \"value\": transaction_result[0],
                \"unit\": \"\",
                \"type\": \"counter\"
            }
            
            metrics[\"db.transaction.rollback_total\"] = {
                \"value\": transaction_result[1],
                \"unit\": \"\",
                \"type\": \"counter\"
            }
            
            # Calculate TPS (if we have previous metrics)
            if self.last_metrics:
                time_delta = time.time() - self.last_metrics['timestamp']
                commits_delta = transaction_result[0] - self.last_metrics['transactions'][0]
                tps = commits_delta / time_delta if time_delta > 0 else 0
                metrics[\"db.transaction.tps\"] = {
                    \"value\": tps,
                    \"unit\": \"transactions/sec\",
                    \"type\": \"gauge\"
                }
            
            # Cache metrics
            cache_query = \"\"\"SELECT 
                sum(blks_hit) as hits,
                sum(blks_read) as reads
                FROM pg_stat_database\"\"\"
            cache_result = self.adapter.execute(cache_query)[0]
            
            if cache_result[0] + cache_result[1] > 0:
                hit_ratio = cache_result[0] / (cache_result[0] + cache_result[1])
            else:
                hit_ratio = 0
            
            metrics[\"db.cache.hit_ratio\"] = {
                \"value\": hit_ratio,
                \"unit\": \"percent\",
                \"type\": \"gauge\"
            }
            
            # WAL metrics
            wal_query = \"SELECT pg_current_wal_lsn() - pg_current_wal_insert_lsn() as wal_bytes\"
            wal_bytes = self.adapter.execute(wal_query)[0][0]
            metrics[\"db.wal.bytes\"] = {
                \"value\": int(wal_bytes),
                \"unit\": \"bytes\",
                \"type\": \"counter\"
            }
            
            # Lock metrics
            lock_query = \"SELECT COUNT(*) FROM pg_locks WHERE granted = true\"
            lock_count = self.adapter.execute(lock_query)[0][0]
            metrics[\"db.lock.count\"] = {
                \"value\": lock_count,
                \"unit\": \"\",
                \"type\": \"gauge\"
            }
            
            # Database info tags
            if 'version' in db_info:
                metrics[\"db.version\"] = {
                    \"value\": db_info['version'].split()[0] if ' ' in db_info['version'] else db_info['version'],
                    \"unit\": \"\",
                    \"type\": \"gauge\",
                    \"tags\": {\"database\": \"postgresql\"}
                }
            
            # Store current metrics for TPS calculation
            self.last_metrics = {
                'timestamp': time.time(),
                'transactions': transaction_result
            }
            
        except Exception as e:
            print(f\"Warning: Failed to collect some database metrics: {e}\")
        
        return metrics
    
    def create_metric_objects(self) -> List[Metric]:
        \"\"\"Convert collected metrics to Metric objects.\"\"\"
        metrics_data = self.collect_metrics()
        timestamp = time.time()
        metric_objects = []
        
        for name, data in metrics_data.items():
            tags = data.get(\"tags\", {})
            metric = Metric(
                timestamp=timestamp,
                metric_name=name,
                metric_type=MetricType(data[\"type\"]),
                value=data[\"value\"],
                unit=data[\"unit\"],
                source=MetricSource.DATABASE,
                tags=tags
            )
            metric_objects.append(metric)
        
        return metric_objects
