##  观察指标

* Metric
   |
   * timestamp
   * name
   * type
   * value
   * unit
   * source
   * tags



## 包含

* Gauge

* Counter

* Histogram

* Metric naming convention

* Time series设计

* JSONL格式

* Prometheus兼容设计

# Database Metrics Design


## Metric Model


Every metric:


timestamp

name

type

value

unit

source

tags



---

## Metric Type


Gauge:


instant value



Example:


CPU


connections



Counter:


monotonic increasing



Example:


transactions


WAL bytes



Histogram:


distribution



Example:


latency percentile