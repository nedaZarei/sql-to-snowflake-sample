# Sample Fund Analytics — PostgreSQL to Snowflake Translation Demo

A fully working dbt project built on PostgreSQL, designed as a sample for translating and optimizing SQL from PostgreSQL to Snowflake.

## Project Structure

```
sample-dbt/
├── postgres/                         # Source: fully working PostgreSQL dbt project
│   ├── dbt_project.yml
│   ├── profiles.yml
│   ├── packages.yml
│   ├── docker-compose.yml
│   ├── seeds/                        # 10 CSV seed files (raw data)
│   ├── models/
│   │   ├── staging/                  # 10 models
│   │   ├── intermediate/             # 8 models
│   │   └── marts/                    # 10 models (5 FACTs + 5 REPORTs)
│   ├── macros/                       # 2 macro files (intentionally underused)
│   ├── tests/                        # 1 custom data test
│   └── schemas/
│       ├── generate_schemas.py       # Connects to live PG, extracts schema docs
│       └── all_schemas_postgres.md   # Auto-generated: 10 tables, 28 views
│
└── snowflake/                        # Target: Artemis fills this after translation
    └── schemas/
        └── generate_schemas.py       # Ready to run against Snowflake
```

**28 models | 53 tests | All passing**

## Quick Start

```bash
cd postgres/

# Start PostgreSQL
docker-compose up -d

# Install dbt dependencies
dbt deps

# Load seed data
dbt seed

# Run all models
dbt run

# Run all tests
dbt test
```

## Three Pipelines

### Pipeline A — Simple (4 models)

**Path:** `stg_portfolios`, `stg_positions` -> `fact_portfolio_summary` -> `report_portfolio_overview`

- Basic joins and aggregations
- Anti-patterns: unnecessary DISTINCT, late filtering

### Pipeline B — Medium (8 models)

**Path:** `stg_trades`, `stg_instruments`, `stg_counterparties`, `stg_dates` -> `int_trade_enriched`, `int_daily_positions` -> `fact_portfolio_pnl`, `fact_trade_activity` -> `report_daily_pnl`

- Window functions for running PnL
- Anti-patterns: repeated joins across FACTs, subqueries instead of QUALIFY, deep CTEs

### Pipeline C — Complex (15+ models)

**Path:** `stg_cashflows`, `stg_valuations`, `stg_benchmarks`, `stg_fund_structures`, `stg_portfolios`, `stg_dates` -> `int_cashflow_enriched`, `int_valuation_enriched`, `int_benchmark_returns`, `int_fund_nav`, `int_portfolio_attribution`, `int_irr_calculations` -> `fact_fund_performance`, `fact_cashflow_waterfall`, `fact_portfolio_attribution` -> `report_ic_dashboard`, `report_lp_quarterly`

- Heavy window functions (IRR approximation, rolling returns)
- Anti-patterns: duplicated logic across models, expensive joins repeated, all views (should be tables), non-Snowflake patterns

## Intentional Anti-Patterns

This project contains deliberate anti-patterns that represent real-world optimization opportunities:

| Anti-Pattern | Where | Optimization Opportunity |
|---|---|---|
| Duplicated fiscal quarter logic | 6+ staging/mart models | Consolidate into macro |
| Macros exist but aren't used | `financial_calculations.sql` | Replace inline logic with macro calls |
| PostgreSQL-specific date syntax | `date - date`, `date_trunc`, `extract` | Translate to Snowflake equivalents |
| Subquery deduplication | `int_trade_enriched`, reports | Replace with `QUALIFY` |
| All models materialized as views | `dbt_project.yml` | Use tables for facts, incremental where appropriate |
| Deep CTE nesting (5-6 levels) | `int_irr_calculations`, `int_daily_positions` | Simplify to fewer passes |
| Repeated expensive joins | `fact_portfolio_pnl` re-does `int_trade_enriched` joins | Reuse intermediate models |
| Running totals computed multiple times | Intermediate + mart layers | Compute once upstream |

## Schema Documentation

The `schemas/` folders contain Python scripts that connect to the live database and auto-generate Markdown documentation with column types, row counts, PKs, FKs, and view definitions.

- **PostgreSQL:** `postgres/schemas/all_schemas_postgres.md` (pre-generated)
- **Snowflake:** Run `snowflake/schemas/generate_schemas.py` after translation

## Domain

The project models a fund management analytics platform with:
- **Portfolios** across hedge fund and private equity strategies
- **Trades** with counterparty and instrument enrichment
- **Valuations** with NAV tracking and period-over-period analysis
- **Cashflows** with waterfall and carry calculations
- **Benchmarks** with rolling return comparisons
- **Fund structures** with IRR approximation and TVPI/DPI multiples
