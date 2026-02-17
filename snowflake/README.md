# Snowflake Target

This folder is the target for the translated dbt project.

After Artemis translates the PostgreSQL project in `../postgres/` to Snowflake, place the resulting dbt project here.

## Schema Documentation

Once the translated project is deployed and running on Snowflake, generate schema documentation:

```bash
# Set required environment variables
export SNOWFLAKE_ACCOUNT=<your-account>
export SNOWFLAKE_USER=<your-user>
export SNOWFLAKE_PASSWORD=<your-password>

# Optional overrides (defaults shown)
export SNOWFLAKE_WAREHOUSE=COMPUTE_WH
export SNOWFLAKE_DATABASE=SAMPLE_FUND_ANALYTICS
export SNOWFLAKE_ROLE=ACCOUNTADMIN
export SNOWFLAKE_SCHEMA=DEV

# Generate documentation
pip install snowflake-connector-python
python schemas/generate_schemas.py
```

This produces `schemas/all_schemas_snowflake.md` documenting all translated models.
