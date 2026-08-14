"""
1. 生成的文件名 generate_metric_report.py
2.  负责：
	输入：
	metrics.jsonl
	输出:
	HTML Report
	包含：
	TPS
	QPS
	latency
	CPU
	IO
	DB指标趋势
	bottleneck summary
"""
import json


def generate(input_file):

    metrics=[]


    with open(input_file) as f:

        for line in f:

            metrics.append(
                json.loads(line)
            )


    html="""

    <html>

    <h1>
    Benchmark Report
    </h1>


    </html>

    """


    open(
    "report.html",
    "w"
    ).write(html)
