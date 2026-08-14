## 观察的指标

* benchmark生命周期

* workload设计

* OLTP

* OLAP

* TPC-C/TPC-H思想

* warmup

* steady state

* repeatability

* 基准测试误差控制



# Database Benchmark Methodology


## Benchmark Lifecycle


Preparation

↓

Warmup

↓

Measurement

↓

Analysis



---

# Preparation


Must define:


Database version

Hardware

Dataset size

Workload


---

# Warmup


Purpose:


- fill cache
- stabilize execution plan


---

# Measurement


Collect:


Performance:


TPS

QPS

Latency


Resource:


CPU

Memory

IO



---

# Benchmark Rules


Never compare:


different hardware


different dataset


different workload