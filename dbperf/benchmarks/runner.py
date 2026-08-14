import time
import logging
import yaml
from typing import Dict, Any, Optional
from datetime import datetime
from .models import BenchmarkConfig, BenchmarkResult, BenchmarkStatus
from .adapters.base import DatabaseAdapter
from .adapters.postgresql import PostgreSQLAdapter
from .workloads.config import WorkloadConfig
from .workloads.factory import WorkloadFactory
from .metrics.manager import MetricsManager
from .reports.generator import ReportGenerator


class BenchmarkRunner:
    """
    Core benchmark execution engine.
    Orchestrates the complete benchmark lifecycle.
    """
    
    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.adapter: Optional[DatabaseAdapter] = None
        self.metrics_manager: Optional[MetricsManager] = None
        self.workload_config: Optional[WorkloadConfig] = None
        self.workload = None
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.status = BenchmarkStatus.PENDING
        
    def setup(self) -> None:
        """Setup benchmark environment."""
        self.logger.info(f"Setting up benchmark: {self.config.name}")
        self.status = BenchmarkStatus.PENDING
        
        # Initialize database adapter
        if self.config.target_database == "postgresql":
            self.adapter = PostgreSQLAdapter(self.config.database_dsn)
        else:
            raise ValueError(f"Unsupported database: {self.config.target_database}")
        
        # Validate database connection
        if not self.adapter.validate_connection():
            raise ConnectionError(f"Cannot connect to database: {self.config.database_dsn}")
        
        # Initialize metrics manager
        self.metrics_manager = MetricsManager(self.adapter)
        
        # Create workload configuration
        self.workload_config = self._create_workload_config()
        
        # Create workload instance
        self.workload = WorkloadFactory.create_workload(
            self.workload_config, self.adapter
        )
        
        self.logger.info("Benchmark setup completed successfully")
    
    def execute(self) -> BenchmarkResult:
        """Execute the complete benchmark."""
        try:
            self.start_time = datetime.now()
            self.logger.info(f"Starting benchmark: {self.config.name}")
            
            # Setup benchmark
            self.setup()
            
            # Warmup phase
            self.logger.info("Starting warmup phase")
            self.status = BenchmarkStatus.WARMUP
            self._execute_warmup()
            
            # Measurement phase
            self.logger.info("Starting measurement phase")
            self.status = BenchmarkStatus.MEASUREMENT
            result = self._execute_measurement()
            
            # Analysis phase
            self.logger.info("Starting analysis phase")
            self.status = BenchmarkStatus.ANALYSIS
            self._analyze_results(result)
            
            self.end_time = datetime.now()
            result.end_time = self.end_time
            
            self.status = BenchmarkStatus.COMPLETED
            self.logger.info(f"Benchmark completed successfully: {self.config.name}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Benchmark failed: {str(e)}")
            self.status = BenchmarkStatus.FAILED
            self.end_time = datetime.now()
            raise
    
    def _create_workload_config(self) -> WorkloadConfig:
        """
        Create workload configuration from benchmark config.
        This is a simplified version - in practice, you'd load this from files.
        """
        from .workloads.config import QueryTemplate, QueryType
        
        # Create basic query templates based on workload type
        if self.config.workload_type == "oltp":
            templates = [
                QueryTemplate(
                    query_type=QueryType.SELECT,
                    template="SELECT * FROM users WHERE id = ?",
                    weight=0.6
                ),
                QueryTemplate(
                    query_type=QueryType.INSERT,
                    template="INSERT INTO users (name, email) VALUES (?, ?)",
                    weight=0.2
                ),
                QueryTemplate(
                    query_type=QueryType.UPDATE,
                    template="UPDATE users SET last_login = NOW() WHERE id = ?",
                    weight=0.2
                )
            ]
        elif self.config.workload_type == "olap":
            templates = [
                QueryTemplate(
                    query_type=QueryType.SELECT,
                    template="SELECT product_category, SUM(amount) FROM orders GROUP BY product_category",
                    weight=1.0
                )
            ]
        else:
            raise ValueError(f"Unknown workload type: {self.config.workload_type}")
        
        return WorkloadConfig(
            name=f"{self.config.name}_{self.config.workload_type}",
            workload_type=self.config.workload_type,
            query_templates=templates,
            think_time_ms=50,
            iterations=self.config.duration_minutes * 60,  # Convert minutes to iterations
            concurrent_users=self.config.concurrent_users,
            warmup_iterations=self.config.warmup_minutes * 60
        )
    
    def _execute_warmup(self) -> None:
        """
        Execute warmup phase.
        Purpose: Fill database cache and stabilize execution plans.
        """
        self.logger.info(f"Executing warmup for {self.config.warmup_minutes} minutes")
        
        # Start metrics collection
        if self.metrics_manager:
            self.metrics_manager.start_collection("warmup_metrics.jsonl")
        
        try:
            # Execute warmup workload
            warmup_result = self.workload.execute()
            
            # Stop warmup metrics
            if self.metrics_manager:
                self.metrics_manager.stop_collection()
            
            self.logger.info("Warmup phase completed")
            
        except Exception as e:
            self.logger.error(f"Warmup phase failed: {str(e)}")
            raise
    
    def _execute_measurement(self) -> BenchmarkResult:
        """
        Execute measurement phase.
        Collect performance metrics during actual workload execution.
        """
        self.logger.info(f"Executing measurement for {self.config.duration_minutes} minutes")
        
        # Start metrics collection
        if self.metrics_manager:
            self.metrics_manager.start_collection("measurement_metrics.jsonl")
        
        try:
            # Execute measurement workload
            measurement_result = self.workload.execute()
            
            # Stop metrics collection
            if self.metrics_manager:
                self.metrics_manager.stop_collection()
            
            # Calculate duration
            duration_seconds = (self.end_time - self.start_time).total_seconds() if self.end_time else 0
            
            # Create benchmark result
            result = BenchmarkResult(
                benchmark_id=self.config.name,
                start_time=self.start_time,
                end_time=self.end_time or datetime.now(),
                duration_seconds=duration_seconds,
                system_metrics=None,  # Would be calculated from metrics
                database_metrics=None,  # Would be calculated from metrics
                workload_metrics=None,  # Would be calculated from metrics
                summary=self._generate_summary(measurement_result),
                bottlenecks=[],
                recommendations=[]
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Measurement phase failed: {str(e)}")
            raise
    
    def _analyze_results(self, result: BenchmarkResult) -> None:
        """
        Analyze benchmark results and identify bottlenecks.
        """
        self.logger.info("Analyzing benchmark results")
        
        # Get workload summary
        workload_summary = self.metrics_manager.get_workload_summary() if self.metrics_manager else {}
        
        # Update result with summary
        result.summary.update(workload_summary)
        
        # Analyze bottlenecks (simplified analysis)
        bottlenecks = []
        recommendations = []
        
        if "tps" in result.summary and result.summary["tps"] < 100:
            bottlenecks.append("Low transaction processing rate")
            recommendations.append("Consider increasing database resources or optimizing queries")
        
        if "error_rate" in result.summary and result.summary["error_rate"] > 0.01:
            bottlenecks.append("High error rate detected")
            recommendations.append("Check database logs for connection or query errors")
        
        # Update result with analysis
        result.bottlenecks = bottlenecks
        result.recommendations = recommendations
        
        self.logger.info(f"Analysis completed: {len(bottlenecks)} bottlenecks identified")
    
    def _generate_summary(self, measurement_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a summary of the benchmark execution.
        """
        duration = measurement_result.get("end_time", 0) - measurement_result.get("start_time", 0)
        total_queries = measurement_result.get("total_queries", 0)
        successful_queries = measurement_result.get("successful_queries", 0)
        failed_queries = measurement_result.get("failed_queries", 0)
        
        tps = total_queries / duration if duration > 0 else 0
        error_rate = failed_queries / total_queries if total_queries > 0 else 0
        
        return {
            "duration_seconds": duration,
            "total_queries": total_queries,
            "successful_queries": successful_queries,
            "failed_queries": failed_queries,
            "tps": tps,
            "error_rate": error_rate,
            "status": "completed" if failed_queries < total_queries * 0.01 else "degraded"
        }
    
    def generate_report(self, output_dir: str = "reports") -> str:
        """
        Generate benchmark report.
        """
        if self.status != BenchmarkStatus.COMPLETED:
            raise RuntimeError("Cannot generate report for incomplete benchmark")
        
        generator = ReportGenerator()
        return generator.generate_report(self, output_dir)


def load_benchmark_config(config_path: str) -> BenchmarkConfig:
    """
    Load benchmark configuration from YAML file.
    """
    with open(config_path, 'r') as f:
        config_data = yaml.safe_load(f)
    
    return BenchmarkConfig(
        name=config_data["name"],
        description=config_data.get("description", ""),
        database_dsn=config_data["database_dsn"],
        workload_type=config_data["workload_type"],
        duration_minutes=config_data["duration_minutes"],
        warmup_minutes=config_data.get("warmup_minutes", 5),
        concurrent_users=config_data["concurrent_users"],
        query_mix=config_data.get("query_mix", {}),
        target_database=config_data.get("target_database", "postgresql")
    )
