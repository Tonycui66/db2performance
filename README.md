# Database Performance Engineering Framework

A comprehensive database performance testing and observability framework built with Python 3.12.

## Features

- **Modular Architecture**: Clean separation of concerns with adapters, workloads, metrics, and reports
- **Multiple Database Support**: PostgreSQL with extensible adapter pattern
- **Workload Types**: OLTP, OLAP, and mixed workloads
- **Comprehensive Metrics**: System, database, and workload metrics collection
- **Real-time Monitoring**: Live metrics collection during benchmarks
- **Detailed Reports**: HTML, JSON, and summary reports
- **CLI Interface**: Easy-to-use command-line interface

## Quick Start

### Installation

`ash
cd database-performance-engineer
pip install -e .
`

### Setup Database

1. Start PostgreSQL database
2. Create test database:
   `ash
   createdb testdb
   `
3. Initialize schema:
   `ash
   psql -d testdb -f examples/database_schema.sql
   `

### Run a Benchmark

`ash

# Generate configuration

dbperf generate-config --workload-type oltp_mixed --output config/

# Run benchmark

dbperf run --config config/oltp_mixed_config.yaml --output reports/
`

### Test Connection

`ash
dbperf test-connection --dsn "postgresql://postgres:postgres@localhost:5432/testdb"
`

## Architecture

`
dbperf/
©À©¤©¤ adapters/          # Database adapters
©¦   ©À©¤©¤ base.py       # Abstract base class
©¦   ©¸©¤©¤ postgresql.py # PostgreSQL implementation
©À©¤©¤ workloads/         # Workload implementations
©¦   ©À©¤©¤ config.py     # Workload configuration
©¦   ©À©¤©¤ impl.py       # OLTP/OLAP implementations
©¦   ©¸©¤©¤ factory.py    # Workload factory and generators
©À©¤©¤ metrics/          # Metrics collection
©¦   ©À©¤©¤ system.py     # System metrics
©¦   ©À©¤©¤ database.py   # Database metrics
©¦   ©À©¤©¤ workload.py   # Workload metrics
©¦   ©¸©¤©¤ manager.py    # Metrics coordination
©À©¤©¤ benchmarks/       # Benchmark execution
©¦   ©¸©¤©¤ runner.py     # Benchmark runner
©À©¤©¤ reports/          # Report generation
©¦   ©¸©¤©¤ generator.py  # Report generator
©À©¤©¤ models.py         # Data models
©¸©¤©¤ cli.py           # Command-line interface
`

## Configuration

### Benchmark Configuration

`yaml
name: "oltp_benchmark"
description: "OLTP database performance benchmark"
database_dsn: "postgresql://postgres:postgres@localhost:5432/testdb"
workload_type: "oltp"
duration_minutes: 10
warmup_minutes: 5
concurrent_users: 20
query_mix:
  select: 0.6
  insert: 0.2
  update: 0.2
target_database: "postgresql"
`

### Workload Types

#### OLTP Workloads

- oltp_read_heavy: Read-heavy transactional workload
- oltp_mixed: Balanced read/write operations
- pc_c_like: TPC-C like e-commerce workload

#### OLAP Workloads

- olap_analytical: Complex analytical queries

## Metrics

### System Metrics

- CPU usage and load average
- Memory usage
- Disk I/O statistics
- Network I/O statistics

### Database Metrics

- Connection count
- Transaction statistics
- Cache hit ratio
- WAL statistics
- Lock contention

### Workload Metrics

- TPS (transactions per second)
- QPS (queries per second)
- Latency percentiles (p50, p95, p99)
- Error rate

## Reports

The framework generates three types of reports:

1. **HTML Report**: Comprehensive visual report with charts and summaries
2. **JSON Report**: Machine-readable data format for analysis
3. **Summary Report**: Plain text summary for quick review

## Development

### Running Tests

`ash
pytest tests/
`

### Code Quality

`ash
black dbperf/
flake8 dbperf/
mypy dbperf/
`

## Example Usage

`python
from dbperf.benchmarks import BenchmarkRunner, load_benchmark_config
from dbperf.workloads.factory import WorkloadGenerator

# Load configuration

config = load_benchmark_config('config/oltp_benchmark.yaml')

# Create benchmark runner

runner = BenchmarkRunner(config)

# Run benchmark

result = runner.execute()

# Generate report

report_file = runner.generate_report('reports/')
`

## Extending the Framework

### Adding New Database Adapters

1. Create a new adapter class extending DatabaseAdapter
2. Implement all abstract methods
3. Register with the factory

### Adding New Workload Types

1. Create workload class extending base workload
2. Register with WorkloadFactory
3. Add to CLI commands

### Adding New Metrics

1. Extend appropriate metrics collector
2. Update data models
3. Update report generation

## Requirements

- Python 3.12+
- PostgreSQL 12+
- Docker (for containerized deployment)

## License

MIT License
