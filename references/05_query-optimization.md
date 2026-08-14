## content

* Explain Plan

* Cost模型

* Seq Scan

* Index Scan

* Bitmap Scan

* Join算法

* SQL慢查询定位

* pg_stat_statements分析

# Query Optimization Guide


## EXPLAIN ANALYZE


Always analyze:


execution plan

actual rows

cost


---

## Common Problems


Sequential Scan


Cause:


missing index


large scan



---

Lock contention:


Check:


pg_locks


---

Slow SQL:


Use:


pg_stat_statements