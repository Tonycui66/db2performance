import json
import os
from typing import Dict, Any, List
from datetime import datetime
from ..models import BenchmarkResult


class ReportGenerator:
    \"\"\"
    Generates comprehensive benchmark reports.
    \"\"\"
    
    def generate_report(self, benchmark_result: BenchmarkResult, output_dir: str = \"reports\") -> str:
        \"\"\"
        Generate a comprehensive benchmark report.
        \"\"\"
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate different report formats
        html_file = self._generate_html_report(benchmark_result, output_dir)
        json_file = self._generate_json_report(benchmark_result, output_dir)
        summary_file = self._generate_summary_report(benchmark_result, output_dir)
        
        return html_file
    
    def _generate_html_report(self, result: BenchmarkResult, output_dir: str) -> str:
        \"\"\"
        Generate HTML report.
        \"\"\"
        html_content = f\"\"\"
<!DOCTYPE html>
<html>
<head>
    <title>Benchmark Report - {result.benchmark_id}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ margin: 20px 0; padding: 15px; background-color: #e8f4f8; border-radius: 5px; }}
        .metrics {{ margin: 20px 0; }}
        .metric {{ margin: 10px 0; padding: 10px; background-color: #f9f9f9; border-radius: 3px; }}
        .bottlenecks {{ margin: 20px 0; padding: 15px; background-color: #ffeaa7; border-radius: 5px; }}
        .recommendations {{ margin: 20px 0; padding: 15px; background-color: #d1f2eb; border-radius: 5px; }}
        .footer {{ margin-top: 30px; padding: 20px; background-color: #f0f0f0; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class=\"header\">
        <h1>Database Performance Benchmark Report</h1>
        <h2>{result.benchmark_id}</h2>
        <p><strong>Start Time:</strong> {result.start_time}</p>
        <p><strong>Duration:</strong> {result.duration_seconds:.2f} seconds</p>
        <p><strong>Status:</strong> {'Completed' if result.bottlenecks else 'Success'}</p>
    </div>
    
    <div class=\"summary\">
        <h3>Summary</h3>
        <div class=\"metric\">
            <strong>Total Queries:</strong> {result.summary.get('total_queries', 0)}
        </div>
        <div class=\"metric\">
            <strong>TPS:</strong> {result.summary.get('tps', 0):.2f} transactions/sec
        </div>
        <div class=\"metric\">
            <strong>Error Rate:</strong> {result.summary.get('error_rate', 0):.2%}
        </div>
        <div class=\"metric\">
            <strong>Status:</strong> {result.summary.get('status', 'unknown')}
        </div>
    </div>
    
    <div class=\"metrics\">
        <h3>Detailed Metrics</h3>
        {self._generate_metrics_html(result)}
    </div>
    
    {self._generate_bottlenecks_html(result)}
    {self._generate_recommendations_html(result)}
    
    <div class=\"footer\">
        <p>Generated on {datetime.now()}</p>
        <p>Database Performance Engineering Framework</p>
    </div>
</body>
</html>
        \"\"\"
        
        html_file = os.path.join(output_dir, f\"benchmark_{result.benchmark_id}.html\")
        with open(html_file, 'w') as f:
            f.write(html_content)
        
        return html_file
    
    def _generate_metrics_html(self, result: BenchmarkResult) -> str:
        \"\"\"
        Generate metrics section HTML.
        \"\"\"
        metrics_html = \"\"\"
        <div class=\"metric\">
            <strong>Successful Queries:</strong> {result.summary.get('successful_queries', 0)}
        </div>
        <div class=\"metric\">
            <strong>Failed Queries:</strong> {result.summary.get('failed_queries', 0)}
        </div>
        <div class=\"metric\">
            <strong>Duration:</strong> {result.summary.get('duration_seconds', 0):.2f} seconds
        </div>
        \"\"\"
        return metrics_html
    
    def _generate_bottlenecks_html(self, result: BenchmarkResult) -> str:
        \"\"\"
        Generate bottlenecks section HTML.
        \"\"\"
        if not result.bottlenecks:
            return \"\"\"
        <div class=\"bottlenecks\">
            <h3>Bottlenecks Identified</h3>
            <ul>
        \"\"\"
        
        for bottleneck in result.bottlenecks:
            bottlenecks_html += f\"<li>{bottleneck}</li>\\n\"
        
        bottlenecks_html += \"\"\"            </ul>
        </div>\"\"\"
        
        return bottlenecks_html
    
    def _generate_recommendations_html(self, result: BenchmarkResult) -> str:
        \"\"\"
        Generate recommendations section HTML.
        \"\"\"
        if not result.recommendations:
            return \"\"\"
        <div class=\"recommendations\">
            <h3>Optimization Recommendations</h3>
            <ul>
        \"\"\"
        
        for recommendation in result.recommendations:
            recommendations_html += f\"<li>{recommendation}</li>\\n\"
        
        recommendations_html += \"\"\"            </ul>
        </div>\"\"\"
        
        return recommendations_html
    
    def _generate_json_report(self, result: BenchmarkResult, output_dir: str) -> str:
        \"\"\"
        Generate JSON report.
        \"\"\"
        report_data = {
            \"benchmark_id\": result.benchmark_id,
            \"start_time\": result.start_time.isoformat(),
            \"end_time\": result.end_time.isoformat(),
            \"duration_seconds\": result.duration_seconds,
            \"summary\": result.summary,
            \"bottlenecks\": result.bottlenecks,
            \"recommendations\": result.recommendations,
            \"generated_at\": datetime.now().isoformat()
        }
        
        json_file = os.path.join(output_dir, f\"benchmark_{result.benchmark_id}.json\")
        with open(json_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        return json_file
    
    def _generate_summary_report(self, result: BenchmarkResult, output_dir: str) -> str:
        \"\"\"
        Generate summary text report.
        \"\"\"
        summary = f\"\"\"
Database Performance Benchmark Report
=====================================

Benchmark ID: {result.benchmark_id}
Start Time: {result.start_time}
Duration: {result.duration_seconds:.2f} seconds

Summary:
- Total Queries: {result.summary.get('total_queries', 0)}
- Successful Queries: {result.summary.get('successful_queries', 0)}
- Failed Queries: {result.summary.get('failed_queries', 0)}
- TPS: {result.summary.get('tps', 0):.2f} transactions/sec
- Error Rate: {result.summary.get('error_rate', 0):.2%}
- Status: {result.summary.get('status', 'unknown')}

Bottlenecks:
{chr(10).join(f\"- {bottleneck}\" for bottleneck in result.bottlenecks)}

Recommendations:
{chr(10).join(f\"- {recommendation}\" for recommendation in result.recommendations)}

Generated: {datetime.now()}
\"\"\"
        
        summary_file = os.path.join(output_dir, f\"benchmark_{result.benchmark_id}_summary.txt\")
        with open(summary_file, 'w') as f:
            f.write(summary)
        
        return summary_file
