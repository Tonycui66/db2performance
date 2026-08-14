import click
import logging
import yaml
import sys
from pathlib import Path
from .benchmarks import BenchmarkRunner, load_benchmark_config
from .workloads.factory import WorkloadGenerator


def setup_logging(verbose: bool = False):
    \"\"\"
    Setup logging configuration.
    \"\"\"
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('benchmark.log')
        ]
    )


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def cli(verbose):
    \"\"\"
    Database Performance Engineering CLI
    \"\"\"
    setup_logging(verbose)


@cli.command()
@click.option('--config', '-c', required=True, help='Benchmark configuration file')
@click.option('--output', '-o', default='reports', help='Output directory for reports')
def run(config, output):
    \"\"\"
    Run a benchmark.
    \"\"\"
    try:
        # Load configuration
        click.echo(f\"Loading benchmark configuration from {config}\")
        benchmark_config = load_benchmark_config(config)
        
        # Validate configuration
        if not benchmark_config.validate():
            click.echo(\"Error: Invalid benchmark configuration\", err=True)
            sys.exit(1)
        
        click.echo(f\"Starting benchmark: {benchmark_config.name}\")
        
        # Create and run benchmark
        runner = BenchmarkRunner(benchmark_config)
        result = runner.execute()
        
        # Generate report
        click.echo(f\"Generating report in {output} directory\")
        report_file = runner.generate_report(output)
        
        click.echo(f\"Benchmark completed successfully!\")
        click.echo(f\"Report generated: {report_file}\")
        
        # Print summary
        if result.summary:
            click.echo(\"\\nBenchmark Summary:\")
            click.echo(f\"  Total Queries: {result.summary.get('total_queries', 0)}\")
            click.echo(f\"  TPS: {result.summary.get('tps', 0):.2f}\")
            click.echo(f\"  Error Rate: {result.summary.get('error_rate', 0):.2%}\")
            
            if result.bottlenecks:
                click.echo(\"\\nBottlenecks:\")
                for bottleneck in result.bottlenecks:
                    click.echo(f\"  - {bottleneck}\")
            
            if result.recommendations:
                click.echo(\"\\nRecommendations:\")
                for recommendation in result.recommendations:
                    click.echo(f\"  - {recommendation}\")
    
    except Exception as e:
        click.echo(f\"Error: {str(e)}\", err=True)
        sys.exit(1)


@cli.command()
@click.option('--workload-type', type=click.Choice(['oltp_read_heavy', 'oltp_mixed', 'olap_analytical', 'tpc_c_like']), required=True)
@click.option('--output', '-o', default='config', help='Output directory for configuration')
def generate_config(workload_type, output):
    \"\"\"
    Generate a benchmark configuration file.
    \"\"\"
    try:
        # Generate configuration
        if workload_type == 'oltp_read_heavy':
            workload = WorkloadGenerator.create_oltp_read_heavy_workload()
        elif workload_type == 'oltp_mixed':
            workload = WorkloadGenerator.create_oltp_mixed_workload()
        elif workload_type == 'olap_analytical':
            workload = WorkloadGenerator.create_olap_analytical_workload()
        elif workload_type == 'tpc_c_like':
            workload = WorkloadGenerator.create_tpc_c_workload()
        
        # Create benchmark config
        config = {
            'name': workload.name,
            'description': f'Generated {workload_type} workload',
            'database_dsn': 'postgresql://user:password@localhost:5432/testdb',
            'workload_type': workload.workload_type.value,
            'duration_minutes': 10,
            'warmup_minutes': 5,
            'concurrent_users': workload.concurrent_users,
            'query_mix': {qt.query_type.value: qt.weight for qt in workload.query_templates}
        }
        
        # Save configuration
        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)
        config_file = output_path / f'{workload_type}_config.yaml'
        
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        click.echo(f\"Configuration generated: {config_file}\")
    
    except Exception as e:
        click.echo(f\"Error: {str(e)}\", err=True)
        sys.exit(1)


@cli.command()
@click.option('--workload-type', type=click.Choice(['oltp', 'olap']), required=True)
@click.option('--output', '-o', default='workloads', help='Output directory for workloads')
def generate_workload(workload_type, output):
    \"\"\"
    Generate a workload configuration file.
    \"\"\"
    try:
        if workload_type == 'oltp':
            workload = WorkloadGenerator.create_oltp_mixed_workload()
        elif workload_type == 'olap':
            workload = WorkloadGenerator.create_olap_analytical_workload()
        
        # Save workload configuration
        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)
        workload_file = output_path / f'{workload_type}_workload.yaml'
        
        workload_data = {
            'name': workload.name,
            'workload_type': workload.workload_type.value,
            'think_time_ms': workload.think_time_ms,
            'iterations': workload.iterations,
            'concurrent_users': workload.concurrent_users,
            'warmup_iterations': workload.warmup_iterations,
            'query_templates': [
                {
                    'query_type': qt.query_type.value,
                    'template': qt.template,
                    'weight': qt.weight,
                    'validation_rules': qt.validation_rules
                }
                for qt in workload.query_templates
            ]
        }
        
        with open(workload_file, 'w') as f:
            yaml.dump(workload_data, f, default_flow_style=False)
        
        click.echo(f\"Workload generated: {workload_file}\")
    
    except Exception as e:
        click.echo(f\"Error: {str(e)}\", err=True)
        sys.exit(1)


@cli.command()
def list_workloads():
    \"\"\"
    List available workload generators.
    \"\"\"
    click.echo(\"Available Workload Generators:\")
    click.echo(\"  oltp_read_heavy  - Read-heavy OLTP workload\")
    click.echo(\"  oltp_mixed       - Balanced OLTP workload\")
    click.echo(\"  olap_analytical  - OLAP analytical workload\")
    click.echo(\"  tpc_c_like       - TPC-C like workload\")


@cli.command()
@click.option('--dsn', required=True, help='Database connection string')
def test_connection(dsn):
    \"\"\"
    Test database connection.
    \"\"\"
    try:
        from .adapters.postgresql import PostgreSQLAdapter
        
        adapter = PostgreSQLAdapter(dsn)
        if adapter.validate_connection():
            click.echo(\"Database connection successful!\")
            
            # Get connection info
            info = adapter.get_connection_info()
            click.echo(f\"Database: {info.get('database', 'Unknown')}\")
            click.echo(f\"User: {info.get('user', 'Unknown')}\")
            click.echo(f\"Version: {info.get('version', 'Unknown')}\")
        else:
            click.echo(\"Database connection failed!\", err=True)
            sys.exit(1)
    
    except Exception as e:
        click.echo(f\"Error: {str(e)}\", err=True)
        sys.exit(1)


def main():
    \"\""
    Main entry point for the CLI.
    \"\"\"
    cli()


if __name__ == '__main__':
    main()
