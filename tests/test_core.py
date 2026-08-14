import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from dbperf.models import BenchmarkConfig, Metric, MetricType, MetricSource, DatabaseMetrics, WorkloadMetrics
from dbperf.adapters.postgresql import PostgreSQLAdapter
from dbperf.metrics.manager import MetricsManager
from dbperf.workloads.config import WorkloadConfig, WorkloadType, QueryTemplate, QueryType


class TestBenchmarkConfig:
    def test_valid_config(self):
        config = BenchmarkConfig(
            name=\"test\",
            description=\"Test config\",
            database_dsn=\"postgresql://test:test@localhost/test\",
            workload_type=\"oltp\",
            duration_minutes=10,
            warmup_minutes=5,
            concurrent_users=10,
            query_mix={\"select\": 0.5, \"insert\": 0.5}
        )
        
        assert config.validate() is True
    
    def test_invalid_config(self):
        config = BenchmarkConfig(
            name=\"\",
            description=\"\",
            database_dsn=\"\",
            workload_type=\"oltp\",
            duration_minutes=10,
            warmup_minutes=5,
            concurrent_users=10,
            query_mix={}
        )
        
        assert config.validate() is False


class TestPostgreSQLAdapter:
    @patch('dbperf.adapters.postgresql.psycopg.connect')
    def test_connection_validation(self, mock_connect):
        mock_connect.return_value = Mock()
        
        adapter = PostgreSQLAdapter(\"postgresql://test:test@localhost/test\")
        assert adapter.validate_connection() is True


class TestMetricsManager:
    def test_metrics_manager_initialization(self):
        adapter = Mock()
        metrics_manager = MetricsManager(adapter)
        
        assert metrics_manager.adapter == adapter
        assert metrics_manager.is_collecting is False


class TestWorkloadConfig:
    def test_workload_config_normalization(self):
        templates = [
            QueryTemplate(QueryType.SELECT, \"SELECT * FROM users\", 0.4),
            QueryTemplate(QueryType.INSERT, \"INSERT INTO users VALUES (?)\", 0.6)
        ]
        
        config = WorkloadConfig(
            name=\"test\",
            workload_type=WorkloadType.OLTP,
            query_templates=templates,
            think_time_ms=100,
            iterations=100,
            concurrent_users=5
        )
        
        config.normalize_weights()
        
        # Check that weights sum to 1.0
        total_weight = sum(qt.weight for qt in config.query_templates)
        assert abs(total_weight - 1.0) < 0.001
    
    def test_workload_config_validation(self):
        templates = [
            QueryTemplate(QueryType.SELECT, \"SELECT * FROM users\", 1.0)
        ]
        
        config = WorkloadConfig(
            name=\"test\",
            workload_type=WorkloadType.OLTP,
            query_templates=templates,
            think_time_ms=100,
            iterations=100,
            concurrent_users=5
        )
        
        assert config.validate() is True
        
        # Test invalid config
        config.concurrent_users = 0
        assert config.validate() is False


class TestMetric:
    def test_metric_to_dict(self):
        metric = Metric(
            timestamp=1234567890.0,
            metric_name=\"test.metric\",
            metric_type=MetricType.GAUGE,
            value=42.5,
            unit=\"percent\",
            source=MetricSource.SYSTEM,
            tags={\"env\": \"test\"}
        )
        
        result = metric.to_dict()
        
        assert result[\"timestamp\"] == 1234567890.0
        assert result[\"metric_name\"] == \"test.metric\"
        assert result[\"metric_type\"] == \"gauge\"
        assert result[\"value\"] == 42.5
        assert result[\"unit\"] == \"percent\"
        assert result[\"source\"] == \"system\"
        assert result[\"tags\"] == {\"env\": \"test\"}


class TestWorkloadGenerator:
    def test_create_oltp_read_heavy_workload(self):
        workload = WorkloadGenerator.create_oltp_read_heavy_workload()
        
        assert workload.name == \"oltp_read_heavy\"
        assert workload.workload_type == WorkloadType.OLTP
        assert workload.concurrent_users == 10
        assert len(workload.query_templates) == 3
        
        # Check query weights
        select_weight = sum(qt.weight for qt in workload.query_templates if qt.query_type == QueryType.SELECT)
        assert select_weight == 0.8
    
    def test_create_olap_analytical_workload(self):
        workload = WorkloadGenerator.create_olap_analytical_workload()
        
        assert workload.name == \"olap_analytical\"
        assert workload.workload_type == WorkloadType.OLAP
        assert workload.concurrent_users == 5
        assert workload.think_time_ms == 2000
        
        # All queries should be SELECT for OLAP
        for template in workload.query_templates:
            assert template.query_type == QueryType.SELECT
