import pandas as pd


def model(dbt, session):
    # set length of time considered a churn
    pd.Timedelta(days=2)

    dbt.config(enabled=False, materialized="table", packages=["pandas==2.0.0"])

    orders_relation = dbt.ref("stg_customer")

    # converting a DuckDB Python Relation into a pandas DataFrame
    orders_df = orders_relation.df()

    orders_df.sort_values(by="CREATE_DT", inplace=True)
    orders_df["CREATE_DT"] = orders_df.groupby("customer_id")[
        "CREATE_DT"
    ].shift(1)
    orders_df["next_order_at"] = orders_df.groupby("customer_id")["CREATE_DT"].shift(
        -1
    )
    return orders_df