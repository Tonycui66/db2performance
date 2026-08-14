---
name: database-ci-testing
description: 指导如何将数据库测试（单元测试、集成测试、Schema迁移测试）无缝集成到CI/CD流水线（GitHub Actions、GitLab CI等）中，并提供配置模板、工具选型建议和常见问题排查。
---

# 数据库测试 CI/CD 集成技能

## 触发条件
当用户提到以下关键词时，自动激活本技能：
- “数据库测试”、“DB测试”、“集成测试”
- “CI/CD 数据库”、“流水线数据库测试”
- “GitHub Actions 数据库”、“Testcontainers”
- “迁移测试”、“Schema 测试”、“数据质量测试”

## 核心能力

### 1. 需求分析
首先与用户明确以下关键信息：
- **目标数据库**：PostgreSQL、MySQL、MongoDB等。
- **开发语言/框架**：如Java + Spring Boot、Node.js + Prisma、Go + GORM。
- **现有CI/CD平台**：GitHub Actions、GitLab CI、Jenkins等。
- **测试范围**：应用层的集成测试、纯SQL迁移验证、性能测试或安全测试。

### 2. 工具选型建议
根据用户场景，推荐最合适的工具组合：

| 场景                          | 推荐工具                     |
| ----------------------------- | ---------------------------- |
| 单元/集成测试（需真实数据库） | Testcontainers（多语言支持） |
| 大规模数据集的性能测试        | Neon 分支、Postgres.ai DBLab |
| 数据库变更审查与编排          | Bytebase、Liquibase、Atlas   |
| 数据质量测试（分析工程）      | dbt + dbt测试宏              |
| R语言环境测试                 | dittodb                      |
| Go语言环境测试                | TestDock                     |

并提供简要的理由和官方文档链接。

### 3. 提供可复用的流水线模板
根据用户选定的CI/CD平台，生成具体的 YAML 配置文件。例如：

#### GitHub Actions + Testcontainers (Java/Spring Boot)
```yaml
name: Database Integration Test
on: [pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up JDK 17
        uses: actions/setup-java@v3
        with: java-version: '17'
      - name: Run tests with Testcontainers
        run: ./gradlew test
        env:
          # Testcontainers 会自动启动 Docker 容器，无需额外配置
          TESTCONTAINERS_REUSE_ENABLE: true
```