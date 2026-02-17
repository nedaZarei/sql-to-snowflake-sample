"""
Airflow DAG for the Sample Fund Analytics dbt pipeline.

Orchestrates the full dbt workflow:
  1. Seed raw data into PostgreSQL
  2. Run staging models
  3. Run intermediate models
  4. Run mart models (facts + reports)
  5. Run dbt tests
  
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

DBT_PROJECT_DIR = "/opt/dbt/sample_fund_analytics"

default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="dbt_fund_analytics",
    default_args=default_args,
    description="Run dbt fund analytics pipeline (PostgreSQL)",
    schedule_interval="0 6 * * *",  # Daily at 6 AM UTC
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["dbt", "fund-analytics", "postgresql"],
) as dag:

    # Step 1: Load seed data
    # Anti-pattern: full seed reload every run instead of checking if seeds changed
    seed = BashOperator(
        task_id="dbt_seed",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt seed --full-refresh",
    )

    # Step 2: Source freshness check
    # Anti-pattern: this runs AFTER seeding, not before model execution
    source_freshness = BashOperator(
        task_id="dbt_source_freshness",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt source freshness",
    )

    # Step 3: Run Pipeline A (Simple - 4 models)
    run_pipeline_a = BashOperator(
        task_id="dbt_run_pipeline_a",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt run --select tag:pipeline_a",
    )

    # Step 4: Run Pipeline B (Medium - 8 models)
    # Anti-pattern: runs sequentially after A even though they're independent
    run_pipeline_b = BashOperator(
        task_id="dbt_run_pipeline_b",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt run --select tag:pipeline_b",
    )

    # Step 5: Run Pipeline C (Complex - 15+ models)
    run_pipeline_c = BashOperator(
        task_id="dbt_run_pipeline_c",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt run --select tag:pipeline_c",
    )

    # Step 6: Run all tests
    # Anti-pattern: single monolithic test step instead of testing per-pipeline
    test_all = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt test",
    )

    # Step 7: Generate docs
    generate_docs = BashOperator(
        task_id="dbt_docs_generate",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt docs generate",
    )

    # Anti-pattern: fully sequential execution — pipelines A, B, C could run in parallel
    seed >> source_freshness >> run_pipeline_a >> run_pipeline_b >> run_pipeline_c >> test_all >> generate_docs
