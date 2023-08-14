from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import pandas as pd
import boto3

# function


with DAG(
    'world-information-dag',
    default_args={
        "depends_on_past": False,
        "email": ["hei.miaritiana@gmail.com"],
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    },
    description="A simple tutorial DAG",
    schedule=timedelta(days=1),
    start_date=datetime(2023, 8, 14),
    end_date=datetime(2023,12,31),
    catchup=False,
    tags=["world information"],
) as dag:
    t1 = BashOperator(
        task_id="print_date",
        bash_command="date",
    )