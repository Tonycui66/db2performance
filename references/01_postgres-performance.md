## 操作流程

* PostgreSQL架构

* shared_buffers

* WAL

* checkpoint

* vacuum

* autovacuum

* pg_stat_database

* pg_stat_activity

* pg_stat_statements

* 锁分析

* IO分析

PostgreSQL架构

↓

连接管理

↓

事务模型

↓

缓存机制

↓

WAL机制

↓

锁机制

↓

统计视图

↓

性能诊断方法



# PostgreSQL Performance Guide


## 1. Performance Analysis Model


Database performance depends on:


Application workload

+

Database internal state

+

Hardware resources



Performance analysis must correlate:

Workload

Database

System



---

# 2. Important PostgreSQL Views


## pg_stat_database


Used for:


- transaction statistics
- database activity


Metrics:


xact_commit

xact_rollback

blks_hit

blks_read



---

## pg_stat_activity


Monitor:


- active connections
- waiting queries
- transaction state



Important fields:


state

wait_event

query



---

## pg_stat_statements


Required for SQL analysis.


Collect:


queryid

calls

mean_exec_time

rows



---

# 3. Cache Analysis


Cache hit ratio:


hit_ratio=

blks_hit/

(blks_hit+blks_read)


Low cache hit means:


- insufficient memory
- poor query pattern
- large dataset