from airflow.operators.python import PythonOperator
from airflow import DAG
import os
import sys
from datetime import datetime

# Function to handle sys.path modification and imports


def setup_imports():
    sys.path.insert(0, os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))))
    global reddit_pipeline, upload_s3_pipeline
    from pipelines.reddit_pipeline import reddit_pipeline
    from pipelines.aws_s3_pipeline import upload_s3_pipeline


# function to set up imports
setup_imports()


default_args = {
    'owner': 'Shawn Lartey',
    'start_date': datetime(2024, 7, 25)
}

file_postfix = datetime.now().strftime("%Y%m%d")

dag = DAG(
    dag_id='etl_reddit_pipeline',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False,
    tags=['reddit', 'etl', 'pipeline']
)

# extraction from reddit
extract = PythonOperator(
    task_id='reddit_extraction',
    python_callable=reddit_pipeline,
    op_kwargs={
        'file_name': f'reddit_{file_postfix}',
        'subreddit': 'dataengineering',
        'time_filter': 'day',
        'limit': 100
    },
    dag=dag
)

# upload to s3
upload_s3 = PythonOperator(
    task_id='s3_upload',
    python_callable=upload_s3_pipeline,
    dag=dag
)

extract >> upload_s3
