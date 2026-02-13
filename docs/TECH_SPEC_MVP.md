# InfiniteMarketCap MVP 技术方案（TECH SPEC v0.1）

## 1. 文档目的

- 把 `PRD.md` 中的业务目标转成可执行的工程方案。
- 明确 MVP 的系统边界、数据口径、接口契约与上线标准。
- 供你后续直接拆任务开发（数据/后端/前端）。

## 2. MVP 范围与边界

## 2.1 In Scope

1. 覆盖 Top100 资产（跨 stock/crypto/commodity/etf）。
2. 日级数据刷新（UTC 00:30 固定快照）。
3. 首页看板 + 资产详情页 + 关注资产卡片。
4. 异动检测（7D/30D/60D/90D 涨跌阈值 + 排名变化阈值）。
5. 基础导出（CSV）。

## 2.2 Out of Scope

1. 分钟级实时行情。
2. 新闻自动归因。
3. 机器学习预测模型。

## 3. 总体架构

```text
[Data Sources]
  | (daily pull)
  v
[Ingestion Jobs: Python]
  -> raw tables (DuckDB/Postgres)
  -> normalization + symbol mapping
  -> snapshot tables (daily)
  -> factor tables (returns, rank change, share_in_top_n)
  -> anomaly tables (alerts)
  v
[FastAPI Service]
  -> dashboard endpoints
  -> asset detail endpoints
  -> anomalies/rank movers endpoints
  v
[Next.js Dashboard]
  -> 首页
  -> 资产详情
  -> 导出
```

## 4. 技术选型

- 语言：Python 3.11+
- 存储：
  - 本地开发：DuckDB
  - 部署：PostgreSQL 15+
- 后端：FastAPI
- 前端：Next.js + TypeScript + ECharts
- 调度：GitHub Actions（每日）或系统 Cron
- 包管理：uv 或 poetry（二选一，建议 uv）

## 5. 仓库建议结构

```text
InfiniteMarketCap/
  docs/
    PRD.md
    TECH_SPEC_MVP.md
  backend/
    app/
      main.py
      api/
      services/
      models/
    migrations/
    tests/
  data_pipeline/
    jobs/
      pull_assets.py
      normalize_assets.py
      compute_factors.py
      detect_anomalies.py
    sql/
      schema.sql
      views.sql
    tests/
  frontend/
    src/
      app/
      components/
      lib/
    tests/
  .github/workflows/
    daily-pipeline.yml
    ci.yml
```

## 6. 数据模型（MVP）

## 6.1 维表：`dim_asset`

```sql
CREATE TABLE dim_asset (
  asset_id TEXT PRIMARY KEY,
  symbol TEXT NOT NULL,
  name TEXT NOT NULL,
  asset_type TEXT NOT NULL, -- stock/crypto/commodity/etf/index
  exchange TEXT,
  currency TEXT,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_dim_asset_symbol ON dim_asset(symbol);
CREATE INDEX idx_dim_asset_type ON dim_asset(asset_type);
```

## 6.2 事实表：`fact_asset_snapshot_daily`

```sql
CREATE TABLE fact_asset_snapshot_daily (
  date DATE NOT NULL,
  asset_id TEXT NOT NULL REFERENCES dim_asset(asset_id),
  price_usd NUMERIC(30,10),
  market_cap_usd NUMERIC(30,2) NOT NULL,
  volume_usd NUMERIC(30,2),
  rank_global INT NOT NULL,
  rank_in_type INT,
  source TEXT NOT NULL,
  ingested_at TIMESTAMP NOT NULL DEFAULT NOW(),
  PRIMARY KEY (date, asset_id)
);
CREATE INDEX idx_snapshot_date_rank ON fact_asset_snapshot_daily(date, rank_global);
CREATE INDEX idx_snapshot_asset_date ON fact_asset_snapshot_daily(asset_id, date);
```

## 6.3 聚合表：`agg_topn_daily`

```sql
CREATE TABLE agg_topn_daily (
  date DATE NOT NULL,
  top_n INT NOT NULL, -- 30/50/100/500
  total_market_cap_usd NUMERIC(30,2) NOT NULL,
  top5_share NUMERIC(8,6),
  top10_share NUMERIC(8,6),
  advancers_ratio NUMERIC(8,6),
  median_return_7d NUMERIC(12,8),
  mean_return_7d NUMERIC(12,8),
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  PRIMARY KEY (date, top_n)
);
```

## 6.4 因子表：`fact_asset_factor_daily`

```sql
CREATE TABLE fact_asset_factor_daily (
  date DATE NOT NULL,
  asset_id TEXT NOT NULL REFERENCES dim_asset(asset_id),
  return_7d NUMERIC(12,8),
  return_30d NUMERIC(12,8),
  return_60d NUMERIC(12,8),
  return_90d NUMERIC(12,8),
  mcap_change_30d NUMERIC(12,8),
  rank_change_7d INT,
  rank_change_30d INT,
  rank_change_90d INT,
  share_in_top30 NUMERIC(12,8),
  share_in_top50 NUMERIC(12,8),
  share_in_top100 NUMERIC(12,8),
  share_in_top500 NUMERIC(12,8),
  rel_strength_vs_top100_30d NUMERIC(12,8),
  trend_score NUMERIC(12,8),
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  PRIMARY KEY (date, asset_id)
);
CREATE INDEX idx_factor_date_trend ON fact_asset_factor_daily(date, trend_score DESC);
```

## 6.5 事件表：`fact_anomaly_event`

```sql
CREATE TABLE fact_anomaly_event (
  event_id TEXT PRIMARY KEY,
  date DATE NOT NULL,
  asset_id TEXT NOT NULL REFERENCES dim_asset(asset_id),
  event_type TEXT NOT NULL, -- RETURN_SPIKE/RANK_JUMP/VOL_BREAKOUT/TREND_ACCEL
  severity TEXT NOT NULL,   -- P1/P2/P3
  direction TEXT,           -- UP/DOWN
  trigger_value NUMERIC(16,8),
  threshold_value NUMERIC(16,8),
  context JSONB,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_anomaly_date_severity ON fact_anomaly_event(date, severity);
CREATE INDEX idx_anomaly_asset_date ON fact_anomaly_event(asset_id, date);
```

## 7. 指标定义（MVP 固定版）

1. `share_in_top_n = market_cap(asset) / total_market_cap(top_n)`
2. `rank_change_X = rank_today - rank_{Xdays_ago}`
- 说明：值越小表示排名上升（例如 -5 表示上升 5 名）。
3. `return_X = price_today / price_{Xdays_ago} - 1`
4. `rel_strength_vs_top100_30d = return_30d(asset) - median_return_30d(top100)`
5. `trend_score`（0-100 归一化）
- `trend_score = 0.35*price_momentum + 0.30*rank_momentum + 0.20*rel_strength + 0.15*volatility_regime`

## 8. 异动检测规则（MVP）

## 8.1 触发规则

1. `RETURN_SPIKE_UP`
- 条件：`return_7d >= 10%` 或 `return_30d >= 20%` 或 `return_90d >= 30%`
2. `RETURN_SPIKE_DOWN`
- 条件：`return_7d <= -10%` 或 `return_30d <= -20%` 或 `return_90d <= -30%`
3. `RANK_JUMP_UP`
- 条件：`rank_change_30d <= -5` 或 `rank_change_90d <= -10`
4. `RANK_JUMP_DOWN`
- 条件：`rank_change_30d >= 5` 或 `rank_change_90d >= 10`
5. `TREND_ACCEL`
- 条件：`trend_score >= 75` 且连续 3 天上升

## 8.2 告警分级

1. `P1`
- 同时命中：排名跃升 + 涨幅阈值 或 `trend_score >= 85`
2. `P2`
- 命中任一主规则（return/rank/trend）
3. `P3`
- 边缘触发或首次触发

## 8.3 去噪

1. 同资产同方向 3 天内合并为一条事件（更新持续天数）。
2. 若全市场中位数绝对涨跌 > 6%，阈值上调 25%。

## 9. 数据流水线与调度

## 9.1 每日任务顺序（UTC）

1. `00:30` - pull assets raw data
2. `00:40` - normalize + symbol mapping
3. `00:50` - write snapshot table
4. `01:00` - compute factors/aggregates
5. `01:10` - detect anomalies
6. `01:20` - data quality checks + publish readiness

## 9.2 失败重试策略

1. 每个任务最多重试 3 次（指数退避：1m/5m/15m）。
2. 若关键任务失败，保留上次成功数据并标注 `stale=true`。

## 9.3 数据质量检查（DQ）

1. Top100 行数必须 >= 95，否则失败。
2. `market_cap_usd <= 0` 比例不能超过 1%。
3. 当日 rank 必须唯一（1..N 不重复）。
4. 单资产市值日变化 > +/-80% 时标记异常待审。

## 10. API 设计（FastAPI）

## 10.1 首页接口

1. `GET /api/v1/dashboard/overview?date=YYYY-MM-DD&top_n=100`
- 返回：TopN 总市值、集中度、类别占比、市场温度。

2. `GET /api/v1/dashboard/watchlist?date=YYYY-MM-DD&symbols=GOLD,BTC,ETH,NVDA`
- 返回：关注资产当前值与多周期变化。

3. `GET /api/v1/dashboard/rank-movers?date=YYYY-MM-DD&period=30d&limit=20`
- 返回：排名上升/下降榜单。

4. `GET /api/v1/dashboard/anomalies?date=YYYY-MM-DD&severity=P1,P2`
- 返回：异动事件列表。

## 10.2 资产详情接口

1. `GET /api/v1/assets/{asset_id}/summary?date=YYYY-MM-DD`
2. `GET /api/v1/assets/{asset_id}/timeseries?from=YYYY-MM-DD&to=YYYY-MM-DD`
3. `GET /api/v1/assets/{asset_id}/events?from=YYYY-MM-DD&to=YYYY-MM-DD`

## 10.3 导出接口

1. `GET /api/v1/export/topn?date=YYYY-MM-DD&top_n=100&format=csv`
2. `GET /api/v1/export/watchlist?date=YYYY-MM-DD&symbols=...&format=csv`

## 11. 前端页面与接口映射

## 11.1 首页 `/`

1. 顶部卡片：`overview`
2. Watchlist 区域：`watchlist`
3. 排名变化：`rank-movers`
4. 异动雷达：`anomalies`

## 11.2 资产详情 `/asset/[assetId]`

1. 资产总览：`assets/{id}/summary`
2. 价格/市值/排名图：`assets/{id}/timeseries`
3. 事件时间线：`assets/{id}/events`

## 11.3 可用性要求

1. 首屏渲染 <= 2.5s（本地网络环境下）。
2. 所有图表支持 7D/30D/90D/1Y 切换。

## 12. 性能与容量预估

1. MVP 数据量：
- Top100 * 365 天 * 3-5 张事实表，百万级以下，单库可承载。
2. 查询目标：
- 首页全部接口聚合耗时 < 500ms（缓存命中）
- 资产详情时序 < 700ms

## 13. 监控与运维

## 13.1 系统监控

1. 每日任务成功率。
2. 数据新鲜度（最新快照时间）。
3. API p95 延迟、5xx 比例。

## 13.2 告警渠道

1. GitHub Actions 失败通知（邮件/Slack）。
2. 数据质量失败发送摘要（失败规则 + 影响资产数）。

## 14. 安全与合规

1. API Key 通过环境变量管理，不入库不入 git。
2. 导出接口默认只读，不暴露敏感字段。
3. 日志脱敏（token、密钥）。

## 15. 测试策略

## 15.1 数据层

1. 指标计算单元测试（返回值容差检查）。
2. 异动规则测试（边界值：9.99%/10.00%/10.01%）。
3. 快照完整性测试（主键冲突、空值约束）。

## 15.2 API 层

1. 合约测试（字段、类型、空值）。
2. 错误路径（非法日期、非法 top_n）。

## 15.3 前端层

1. 页面渲染 smoke test。
2. 图表与筛选联动测试。

## 16. 发布计划（建议）

1. Week 1
- 建库 + 数据拉取 + 快照落表。
2. Week 2
- 指标计算 + 异动引擎。
3. Week 3
- FastAPI + 首页看板。
4. Week 4
- 详情页 + 导出 + 监控 + 文档收尾。

## 17. MVP 验收标准（DoD）

1. 连续 7 天每日快照成功率 >= 95%。
2. Gold/BTC/ETH/NVDA 在首页与详情页展示一致。
3. 能查询任意资产 90 天排名变化。
4. 能输出 P1/P2/P3 异动列表并解释触发规则。
5. 导出 CSV 可用于复盘分析。

## 18. 开发优先级待办（可直接建 issue）

1. `data`：建表 SQL + migration。
2. `data`：daily pull + normalize job。
3. `data`：factor compute + anomaly job。
4. `backend`：dashboard 4 个核心接口。
5. `backend`：asset detail 3 个接口。
6. `frontend`：首页四区块渲染。
7. `frontend`：资产详情页图表。
8. `ops`：GitHub Actions 定时流水线。
9. `qa`：数据与接口最小测试集。

