import psutil
import time
import json
from datetime import datetime
from typing import Dict, Any
from ..models import Metric, MetricType, MetricSource, SystemMetrics


class SystemMetricsCollector:
    \"\"\"
    Collects system-level metrics (CPU, Memory, Disk, Network).
    \"\"\"
    
    def __init__(self):
        self.last_disk_stats = None
        self.last_network_stats = None
        self.last_time = time.time()
    
    def collect_current_metrics(self) -> SystemMetrics:
        \"\"\"Collect current system metrics.\"\"\"
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        disk_io = psutil.disk_io_counters()
        network_io = psutil.net_io_counters()
        load_avg = psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0.0
        
        return SystemMetrics(
            cpu_usage=cpu_usage,
            memory_usage=memory_info.percent,
            disk_read_bytes=disk_io.read_bytes if disk_io else 0,
            disk_write_bytes=disk_io.write_bytes if disk_io else 0,
            network_bytes_sent=network_io.bytes_sent if network_io else 0,
            network_bytes_recv=network_io.bytes_recv if network_io else 0,
            load_average=load_avg
        )
    
    def collect_metrics(self) -> Dict[str, Any]:
        \"\"\"Collect metrics in JSONL-compatible format.\"\"\"
        current_time = time.time()
        metrics = {}
        
        # CPU metrics
        metrics.update({
            f\"system.cpu.usage\": {
                \"value\": psutil.cpu_percent(interval=1),
                \"unit\": \"percent\",
                \"type\": \"gauge\"
            },
            f\"system.cpu.load_1m\": {
                \"value\": psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0.0,
                \"unit\": \"\",
                \"type\": \"gauge\"
            }
        })
        
        # Memory metrics
        memory = psutil.virtual_memory()
        metrics.update({
            f\"system.memory.usage\": {
                \"value\": memory.percent,
                \"unit\": \"percent\",
                \"type\": \"gauge\"
            },
            f\"system.memory.total\": {
                \"value\": memory.total,
                \"unit\": \"bytes\",
                \"type\": \"gauge\"
            },
            f\"system.memory.available\": {
                \"value\": memory.available,
                \"unit\": \"bytes\",
                \"type\": \"gauge\"
            }
        })
        
        # Disk metrics
        disk_io = psutil.disk_io_counters()
        if disk_io:
            metrics.update({
                f\"system.disk.read_bytes\": {
                    \"value\": disk_io.read_bytes,
                    \"unit\": \"bytes\",
                    \"type\": \"counter\"
                },
                f\"system.disk.write_bytes\": {
                    \"value\": disk_io.write_bytes,
                    \"unit\": \"bytes\",
                    \"type\": \"counter\"
                },
                f\"system.disk.read_count\": {
                    \"value\": disk_io.read_count,
                    \"unit\": \"\",
                    \"type\": \"counter\"
                },
                f\"system.disk.write_count\": {
                    \"value\": disk_io.write_count,
                    \"unit\": \"\",
                    \"type\": \"counter\"
                }
            })
        
        # Network metrics
        network_io = psutil.net_io_counters()
        if network_io:
            metrics.update({
                f\"system.network.bytes_sent\": {
                    \"value\": network_io.bytes_sent,
                    \"unit\": \"bytes\",
                    \"type\": \"counter\"
                },
                f\"system.network.bytes_recv\": {
                    \"value\": network_io.bytes_recv,
                    \"unit\": \"bytes\",
                    \"type\": \"counter\"
                },
                f\"system.network.packets_sent\": {
                    \"value\": network_io.packets_sent,
                    \"unit\": \"\",
                    \"type\": \"counter\"
                },
                f\"system.network.packets_recv\": {
                    \"value\": network_io.packets_recv,
                    \"unit\": \"\",
                    \"type\": \"counter\"
                }
            })
        
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
                source=MetricSource.SYSTEM,
                tags={}
            )
            metric_objects.append(metric)
        
        return metric_objects
